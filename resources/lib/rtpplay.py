"""
    Scraper for the RTP Play website (https://www.rtp.pt/play).

    The mobile app API used previously now rejects every request with
    "Request not authorized", so everything here is read from the same HTML
    pages and HTML fragments the website itself uses.
"""

import base64
import html
import re
from urllib.parse import unquote, urlencode

import requests

BASE_URL = "https://www.rtp.pt"

# The streaming servers return an empty 204 response to unknown user agents
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

WIDEVINE_LICENSE_URL = "https://lic.drmtoday.com/license-proxy-widevine/cenc/?specConform=true"
WIDEVINE_LICENSE_HEADERS = {
    "x-dt-custom-data": base64.b64encode(b'{"userId":"purchase","sessionId":"p0","merchant":"mog_rtp"}').decode(),
    "Content-Type": "application/octet-stream",
    "User-Agent": USER_AGENT,
}


class Stream:
    def __init__(self, url, manifest=None, drm=False, media_type="video"):
        self.url = url
        self.manifest = manifest  # "hls", "mpd" or None for a progressive file
        self.drm = drm
        self.media_type = media_type
        # Continue watching entry the website would report for this episode
        self.telemetry = None


def _get(path, params=None):
    r = requests.get(BASE_URL + path, params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text


def _text(fragment):
    """Strip tags, unescape entities and collapse whitespace."""
    if fragment is None:
        return ""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def _find(pattern, text, default=""):
    m = re.search(pattern, text, flags=re.S)
    return m.group(1) if m else default


def _absolute(url):
    if url.startswith("//"):
        return "https:" + url
    return url


def _deobfuscate(js):
    """Replace atob(decodeURIComponent([...].join(""))) and decodeURIComponent([...].join("")) with plain strings."""
    def join_parts(m):
        return "".join(re.findall(r'"([^"]*)"', m.group(1)))

    def atob(m):
        return '"' + base64.b64decode(unquote(join_parts(m))).decode() + '"'

    def uri(m):
        return '"' + unquote(join_parts(m)) + '"'

    js = re.sub(r'atob\(\s*decodeURIComponent\(\s*\[(.*?)\]\.join\(""\)\s*\)\s*\)', atob, js, flags=re.S)
    return re.sub(r'decodeURIComponent\(\s*\[(.*?)\]\.join\(""\)\s*\)', uri, js, flags=re.S)


def _player_config(page):
    """Return the deobfuscated script that sets up the main player, minus commented-out decoys."""
    start = page.find('if ($("#player_prog")')
    if start < 0:
        start = page.find("new RTPPlayer")
    end = page.find("</script>", start)
    script = re.sub(r"/\*.*?\*/", "", page[start:end], flags=re.S)
    return _deobfuscate(script)


def _choose_stream(sources, drm, media_type):
    dash = sources.get("dash", "")
    hls = sources.get("hls", "")
    if drm:
        # HLS on DRM content is FairPlay, which only Apple devices support
        if dash.startswith("http"):
            return Stream(dash, "mpd", True, media_type)
        return None
    if hls.startswith("http"):
        return Stream(hls, "hls", False, media_type)
    if dash.startswith("http"):
        return Stream(dash, "mpd", False, media_type)
    return None


# Live

def get_live_channels(kind):
    """
    :param kind: "tv" or "radio"
    :return: list of dicts with key, name, image, logo, onair and progress
    """
    page = _get("/play/direto")
    channels = []
    for block in re.split(r'(?=<span id="(?:tv|radio)-\d+")', page)[1:]:
        if not block.startswith('<span id="{}-'.format(kind)):
            continue
        key = _find(r'href="/play/direto/([^"/?]+)"', block)
        if not key:
            continue
        progress = _find(r'class="bar" style="width:(\d+)%', block)
        channels.append({
            "key": key,
            "name": _text(_find(r'alt="Logo ([^"]*)"', block)) or key,
            "image": _absolute(_find(r'<div class="img-holder">\s*<img[^>]*src="([^"]+)"', block)),
            "logo": _absolute(_find(r'class="ev-logo"[^>]*src="([^"]+)"', block)),
            "onair": _text(_find(r'<h4 class="ev-title-epg">(.*?)</h4>', block)),
            "progress": int(progress) if progress else None,
        })
    return channels


def get_live_stream(key):
    page = _get("/play/direto/" + key)
    config = _player_config(page)
    hls = _find(r'let hls_url = "([^"]*)"', page)
    file_obj = _find(r"file:\s*\{(.*?)\}", config)
    sources = dict(re.findall(r'(\w+)\s*:\s*"([^"]*)"', file_obj))
    sources["hls"] = hls
    drm = re.search(r"\bdrm\s*:\s*true", config) is not None
    media_type = _find(r'mediaType:\s*"(\w+)"', config, "video")
    return _choose_stream(sources, drm, media_type)


# On demand

def get_categories():
    page = _get("/play/programas")
    return [{"slug": slug, "name": _text(name)}
            for slug, name in re.findall(
                r'href="/play/programas/([a-z0-9\-]+)/canal"[^>]*>\s*<div class="meta-data"><h4>(.*?)</h4>', page)]


def _parse_items(fragment):
    """Parse the program/episode tiles used across the site's lists."""
    items = []
    for block in re.split(r'(?=<a href="/play/p\d+/)', fragment)[1:]:
        m = re.match(r'<a href="/play/p(\d+)/(?:e(\d+)/)?([^"]*)"([^>]*)>', block)
        if not m:
            continue
        prog_id, episode_id, slug, attrs = m.groups()
        image = _find(r'<img[^>]*src="([^"]+)"', block)
        items.append({
            "program_id": prog_id,
            "episode_id": episode_id,
            "slug": slug,
            "link_title": _text(_find(r'title="([^"]*)"', attrs)),
            "title": _text(_find(r'class="(?:episode|podcast)-title">(.*?)</(?:p|h4)>', block)),
            "subtitle": _text(_find(r'class="(?:episode-lead|podcast-description)">(.*?)</(?:span|p)>', block)),
            "episode": _text(_find(r'class=["\'](?:episode|episode-number|podcast-episode_number)["\']>(.*?)</(?:div|span)>', block)),
            "date": _text(_find(r'class="(?:episode|podcast)-date">(.*?)</(?:div|span)>', block)).strip(" |"),
            "channel": _text(_find(r'class="channel-name">(.*?)</span>', block)),
            "meta": _text(_find(r'<meta content="([^"]*)"', block)),
            "description": _text(_find(r'<meta name="description" content="([^"]*)"', block)),
            "image": _absolute(image) if image else "",
            "audio": "vod-audio" in attrs or "fa-volume" in block,
        })
    return items


def list_programs(category_id=None, page=1, order="recent"):
    """
    :param order: "recent" (most recently updated first) or "az", as on the website
    :return: programs, each with "updated", the date of its latest episode
    """
    params = {"listtype": order, "type": "all", "page": page}
    if category_id:
        params["listcategory"] = category_id
    programs = _parse_items(_get("/play/bg_l_pg/", params))
    for program in programs:
        # The tile's hidden meta ends with the latest episode's date, e.g. "Portugalex Ep. 178 12 out. 2026"
        program["updated"] = _find(r"(\d{1,2} \S+ \d{4})\s*$", program["meta"])
    return programs


def get_category_id(slug):
    if slug == "tema":
        # "Todos os programas" is the unfiltered list
        return ""
    page = _get("/play/programas/{}/canal".format(slug))
    return _find(r"RTPPLAY\.currentHPListCategory = '(\d+)'", page)


def list_episodes(program_id, page=1):
    return _parse_items(_get("/play/bg_l_ep/", {"listProgram": program_id, "page": page}))


def search(query, page=1):
    return _parse_items(_get("/play/bg_l_s/", {"listQuery": query, "page": page}))


def _site_object(page, call):
    """
    Read the object a page passes to one of the website's account helpers
    (TelemetryByProgramRTPPlay.start or FavoritesRTPPlay.start), in the shape
    the website sends to the account API.
    """
    start = page.find(call + "(")
    if start < 0:
        return None
    block = page[start:page.find("});", start)]
    key = _find(r'\bkey:\s*"([^"]*)"', block)
    fields = _find(r"telemetry_obj\s*:\s*\{(.*?)\}", block)
    if not key or not fields:
        return None
    obj = dict(re.findall(r'(\w+)\s*:\s*"([^"]*)"', fields))
    obj.update(key=key, version="1.1")
    return obj


def get_program_favorite(program_id, slug):
    """The favourites entry for a program, as the website would add it."""
    # Any slug works, but without one the site serves a different page, and
    # the entry links back to whichever slug was requested
    return _site_object(_get("/play/p{}/{}".format(program_id, slug or "programa")), "FavoritesRTPPlay.start")


def get_episode_stream(program_id, episode_id, slug):
    # Without the trailing slug the site serves the program page instead
    page = _get("/play/p{}/e{}/{}".format(program_id, episode_id, slug or "episodio"))
    stream = _episode_stream(page)
    if stream:
        stream.telemetry = _site_object(page, "TelemetryByProgramRTPPlay.start")
    return stream


def _episode_stream(page):
    config = _player_config(page)
    # The script assigns f several times; the last assignment is the real one
    assignments = re.findall(r'var f = (\{.*?\}|"[^"]*")\s*;', config, flags=re.S)
    if not assignments:
        return None
    f = assignments[-1]
    drm = re.search(r"\bdrm\s*:\s*true", config) is not None
    media_type = _find(r'mediaType:\s*"(\w+)"', config, "video")
    if f.startswith('"'):
        url = f.strip('"')
        if re.search(r"\.(mp3|mp4|m4a|aac)(\?|$)", url):
            return Stream(url, None, False, media_type)
        return _choose_stream({"hls": url}, drm, media_type)
    return _choose_stream(dict(re.findall(r'(\w+)\s*:\s*"([^"]*)"', f)), drm, media_type)


def widevine_license_key():
    """License key in the url|headers|body|response format used by inputstream.adaptive."""
    return "{}|{}|R{{SSM}}|".format(WIDEVINE_LICENSE_URL, urlencode(WIDEVINE_LICENSE_HEADERS))


def widevine_drm_legacy():
    """DRM config in the keysystem|license url|headers format of inputstream.adaptive.drm_legacy."""
    return "com.widevine.alpha|{}|{}".format(WIDEVINE_LICENSE_URL, urlencode(WIDEVINE_LICENSE_HEADERS))
