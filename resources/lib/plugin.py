import json
import re
import routing
import logging
import xbmc
import xbmcaddon
from resources.lib import kodiutils
from resources.lib import kodilogging
from xbmcgui import ListItem, Dialog, DialogProgress, Window, INPUT_ALPHANUM
from xbmcplugin import addDirectoryItem, endOfDirectory, setResolvedUrl

from . import rtpplay
from .rtpaccount import Account, LoginError

from urllib.parse import urlencode

from inputstreamhelper import Helper

ADDON = xbmcaddon.Addon()
ICON = ADDON.getAddonInfo("icon")
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0])
# Lists on the website come in pages of 12 (search uses 16)
PAGE_SIZE = 12
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()
account = Account(kodiutils.PROFILE)
# Handed to the service, which reports playback progress for continue watching
PLAYBACK_PROPERTY = "plugin.video.rtpplay.playback"


@plugin.route('/')
def index():
    if account.logged_in:
        favourites = ListItem("[B]{}[/B]".format(kodiutils.get_string(32018)))
        addDirectoryItem(handle=plugin.handle, listitem=favourites, isFolder=True, url=plugin.url_for(favorites))

        watching_item = ListItem("[B]{}[/B]".format(kodiutils.get_string(32019)))
        addDirectoryItem(handle=plugin.handle, listitem=watching_item, isFolder=True, url=plugin.url_for(watching))
    else:
        login_item = ListItem("[B]{}[/B]".format(kodiutils.get_string(32016)))
        addDirectoryItem(handle=plugin.handle, listitem=login_item, isFolder=False, url=plugin.url_for(login))

    livetv = ListItem("[B]{}[/B]".format(kodiutils.get_string(32012)))
    addDirectoryItem(handle=plugin.handle, listitem=livetv, isFolder=True, url=plugin.url_for(live, content='tv'))

    liveradio = ListItem("[B]{}[/B]".format(kodiutils.get_string(32013)))
    addDirectoryItem(handle=plugin.handle, listitem=liveradio, isFolder=True, url=plugin.url_for(live, content='radio'))

    latest = ListItem("[B]{}[/B]".format(kodiutils.get_string(32033)))
    addDirectoryItem(handle=plugin.handle, listitem=latest, isFolder=True,
                     url=plugin.url_for(programs_category, name=kodiutils.get_string(32033), slug="tema",
                                        order="recent", page=1))

    programas = ListItem("[B]{}[/B]".format(kodiutils.get_string(32005)))
    addDirectoryItem(handle=plugin.handle, listitem=programas, isFolder=True, url=plugin.url_for(programs))

    pesquisar = ListItem("[B]{}[/B]".format(kodiutils.get_string(32006)))
    addDirectoryItem(handle=plugin.handle, listitem=pesquisar, isFolder=True, url=plugin.url_for(search))

    endOfDirectory(plugin.handle)


@plugin.route('/search')
def search():
    input_text = Dialog().input(kodiutils.get_string(32007), "", INPUT_ALPHANUM)
    if not input_text:
        endOfDirectory(plugin.handle, succeeded=False)
        return
    return plugin.redirect(f'/search/{input_text}/1')


@plugin.route('/search/<input_text>/<page>')
def search_paged(input_text, page):
    showing_results = ListItem("{} [B]{}[/B]".format(kodiutils.get_string(32008), input_text))
    addDirectoryItem(handle=plugin.handle, listitem=showing_results, isFolder=False, url="")

    results = rtpplay.search(input_text, page=int(page))
    for episode in results:
        add_episode(episode, episode["title"], episode["image"])

    if len(results) >= PAGE_SIZE:
        nextpage = str(int(page) + 1)
        nextpage_listitem = ListItem(
            "[B]{}[/B] - {} {} >>>".format(input_text, kodiutils.get_string(32009), nextpage))
        addDirectoryItem(handle=plugin.handle,
                         listitem=nextpage_listitem,
                         isFolder=True,
                         url=plugin.url_for(search_paged,
                                            input_text=input_text,
                                            page=nextpage))
    endOfDirectory(plugin.handle)


@plugin.route('/live')
def live():
    content_type = plugin.args["content"][0]
    if content_type not in ("tv", "radio"):
        raise Exception("Wrong content type")

    for channel in rtpplay.get_live_channels(content_type):
        name = channel["name"]
        img = channel["image"] or channel["logo"]
        progress = "{}%".format(channel["progress"]) if channel["progress"] is not None else ""

        liz = ListItem("[B][COLOR blue]{}[/COLOR][/B] ({}) [B]{}[/B]".format(
            name,
            channel["onair"],
            progress)
        )
        liz.setArt({"thumb": img,
                    "icon": channel["logo"] or img,
                    "fanart": kodiutils.FANART})
        liz.setProperty('IsPlayable', 'true')
        liz.setInfo("Music" if content_type == "radio" else "Video",
                    infoLabels={"title": channel["onair"]})
        addDirectoryItem(
            plugin.handle,
            plugin.url_for(
                live_play,
                label=name,
                key=channel["key"],
                img=img,
                prog=channel["onair"]
            ), liz, False)
    endOfDirectory(plugin.handle)


@plugin.route('/live/play')
def live_play():
    key = plugin.args["key"][0]
    name = plugin.args["label"][0]
    prog = plugin.args["prog"][0]

    icon = ICON
    if "img" in plugin.args:
        icon = plugin.args["img"][0]

    liz = ListItem("[COLOR blue][B]{}[/B][/COLOR] ({})".format(
        name,
        prog)
    )
    liz.setArt({"thumb": icon, "icon": icon})
    play(liz, rtpplay.get_live_stream(key))


@plugin.route('/programs')
def programs():
    for category in rtpplay.get_categories():
        liz = ListItem(category["name"])
        addDirectoryItem(handle=plugin.handle, listitem=liz, isFolder=True,
                         url=plugin.url_for(programs_order, name=category["name"], slug=category["slug"]))

    endOfDirectory(plugin.handle)


@plugin.route('/programs/order')
def programs_order():
    """The website's two orders for a category: most recently updated, and A-Z."""
    slug = plugin.args["slug"][0]
    cat_name = plugin.args["name"][0]
    cat_id = rtpplay.get_category_id(slug)
    for order, label in (("recent", 32033), ("az", 32034)):
        liz = ListItem(kodiutils.get_string(label))
        addDirectoryItem(handle=plugin.handle, listitem=liz, isFolder=True,
                         url=plugin.url_for(programs_category, name=cat_name, slug=slug,
                                            id=cat_id, order=order, page=1))

    endOfDirectory(plugin.handle)


@plugin.route('/programs/category')
def programs_category():
    page = int(plugin.args["page"][0])
    slug = plugin.args["slug"][0]
    cat_name = plugin.args["name"][0]
    order = plugin.args.get("order", ["recent"])[0]
    # Resolved once and carried along; "all programs" has no id
    if "id" in plugin.args:
        cat_id = plugin.args["id"][0]
    else:
        cat_id = rtpplay.get_category_id(slug)

    pagei = ListItem("[B]{}[/B] - {} {}".format(cat_name, kodiutils.get_string(32009), page))
    pagei.setProperty('IsPlayable', 'false')
    addDirectoryItem(handle=plugin.handle, listitem=pagei, isFolder=False, url="")

    items = rtpplay.list_programs(cat_id, page, order)
    favorite_keys = get_favorite_keys()
    seen = set()
    for program in items:
        # The site sometimes lists the same program twice in a row
        if program["program_id"] in seen:
            continue
        seen.add(program["program_id"])
        title = program["title"] or program["meta"]
        img = program["image"]

        label = title
        if program["updated"]:
            # Shows why "most recent" is in the order it is
            label = "{} [COLOR grey]· {}[/COLOR]".format(title, program["updated"])
        # The link title is "Aceder a <latest episode>"
        latest_episode = re.sub(r"^Aceder a ", "", program["link_title"])

        liz = ListItem(label)
        liz.setArt({"thumb": img,
                    "icon": img,
                    "fanart": kodiutils.FANART})
        liz.setInfo("Video", infoLabels={"plot": latest_episode,
                                         "title": title})
        liz.addContextMenuItems(favorite_context_menu(program["program_id"], program["slug"], favorite_keys))

        addDirectoryItem(
            plugin.handle,
            plugin.url_for(
                programs_episodes,
                title=title,
                img=img,
                prog_id=program["program_id"],
                page=1
            ), liz, True)

    if len(items) >= PAGE_SIZE:
        newpage = str(page + 1)
        nextpage = ListItem("[B]{}[/B] - {} {} >>>".format(cat_name,
                                                           kodiutils.get_string(32009), newpage))
        addDirectoryItem(handle=plugin.handle, listitem=nextpage, isFolder=True,
                         url=plugin.url_for(programs_category, name=cat_name, slug=slug,
                                            id=cat_id, order=order, page=newpage))

    endOfDirectory(plugin.handle)


@plugin.route('/programs/episodes')
def programs_episodes():
    title = plugin.args["title"][0]
    img = plugin.args["img"][0]
    prog_id = plugin.args["prog_id"][0]
    page = int(plugin.args["page"][0])

    pagei = ListItem("[B]{}[/B] - {} {}".format(title, kodiutils.get_string(32009), page))
    pagei.setProperty('IsPlayable', 'false')
    addDirectoryItem(handle=plugin.handle, listitem=pagei, isFolder=False, url="")

    episodes = rtpplay.list_episodes(prog_id, page)
    context_menu = favorite_context_menu(prog_id, episodes[0]["slug"] if episodes else "", get_favorite_keys())
    for episode in episodes:
        add_episode(episode, title, img, context_menu)

    if len(episodes) >= PAGE_SIZE:
        newpage = str(page + 1)
        nextpage = ListItem(
            "[B]{}[/B] - {} {} >>>".format(title, kodiutils.get_string(32009), newpage))
        addDirectoryItem(handle=plugin.handle,
                         listitem=nextpage,
                         isFolder=True,
                         url=plugin.url_for(programs_episodes,
                                            title=title,
                                            img=img,
                                            prog_id=prog_id,
                                            page=newpage))

    endOfDirectory(plugin.handle)


def add_episode(episode, program_title, program_img, context_menu=None):
    label = episode["title"] or episode["meta"] or program_title
    if episode["episode"] and episode["episode"].lower() not in label.lower():
        label = "{} - {}".format(label, episode["episode"])
    if episode["subtitle"]:
        label = "{} - {}".format(label, episode["subtitle"])
    if episode["date"] and episode["date"] not in label:
        label = "{} ({})".format(label, episode["date"])
    img = episode["image"] or program_img

    liz = ListItem(label)
    liz.setArt({"thumb": img,
                "icon": img,
                "fanart": kodiutils.FANART})
    liz.setInfo("Video", infoLabels={"plot": episode["description"] or episode["subtitle"] or episode["link_title"],
                                     "title": label})
    liz.setProperty('IsPlayable', 'true')
    if context_menu:
        liz.addContextMenuItems(context_menu)

    addDirectoryItem(
        plugin.handle,
        plugin.url_for(
            programs_play,
            title=label,
            img=img,
            episode_id=episode["episode_id"],
            prog_id=episode["program_id"],
            slug=episode["slug"]
        ), liz, False)


@plugin.route('/programs/play')
def programs_play():
    title = plugin.args["title"][0]
    img = plugin.args["img"][0]
    episode_id = plugin.args["episode_id"][0]
    prog_id = plugin.args["prog_id"][0]
    slug = plugin.args["slug"][0]

    liz = ListItem(title)
    liz.setArt({"thumb": img, "icon": img})
    stream = rtpplay.get_episode_stream(prog_id, episode_id, slug)
    if stream and stream.telemetry and account.logged_in:
        resume_ms = ask_resume(stream.telemetry, always_resume="resume" in plugin.args)
        if resume_ms is None:
            # Cancelled the resume dialog
            setResolvedUrl(plugin.handle, False, liz)
            return
        Window(10000).setProperty(PLAYBACK_PROPERTY, json.dumps({
            "url": stream.url,
            "telemetry": stream.telemetry,
            "resume_ms": resume_ms,
        }))
    play(liz, stream)


def ask_resume(telemetry, always_resume=False):
    """:return: position to start from in milliseconds, or None if the user cancelled"""
    try:
        progress_ms = account.get_progress(telemetry["key"], telemetry["program_id"])
    except Exception:
        logger.exception("Could not get continue watching position")
        return 0
    if progress_ms < 30000:
        return 0
    if always_resume:
        return progress_ms
    seconds = progress_ms // 1000
    position = "{}:{:02d}:{:02d}".format(seconds // 3600, seconds // 60 % 60, seconds % 60)
    choice = Dialog().contextmenu([kodiutils.get_string(32026).format(position), kodiutils.get_string(32027)])
    if choice < 0:
        return None
    return progress_ms if choice == 0 else 0


# Account

@plugin.route('/account/login')
def login():
    try:
        device = account.start_device_login()
    except Exception:
        logger.exception("Could not start login")
        kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32032))
        return
    message = kodiutils.get_string(32023).format(
        device["verification_uri"].replace("https://", ""), device["user_code"])
    expires = int(device.get("expires_in", 600))
    interval = int(device.get("interval", 5))
    progress = DialogProgress()
    progress.create(kodiutils.get_string(32016), message)
    monitor = xbmc.Monitor()
    try:
        waited = 0
        while waited < expires:
            progress.update(int(100 * waited / expires), message)
            if progress.iscanceled() or monitor.waitForAbort(interval):
                return
            waited += interval
            if account.poll_device_login(device["device_code"]):
                break
        else:
            return
    except Exception:
        logger.exception("Login failed")
        kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32032))
        return
    finally:
        progress.close()
    kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32024).format(account.username))
    xbmc.executebuiltin("Container.Refresh")


@plugin.route('/account/logout')
def logout():
    account.logout()
    kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32025))
    xbmc.executebuiltin("Container.Refresh")


def session_expired():
    kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32029))
    endOfDirectory(plugin.handle, succeeded=False)
    xbmc.executebuiltin("Container.Update({},replace)".format(plugin.url_for(index)))


def get_favorite_keys():
    if not account.logged_in:
        return None
    try:
        return {str(f.get("key")) for f in account.get_favorites()}
    except Exception:
        logger.exception("Could not get favourites")
        return None


def favorite_context_menu(program_id, slug, favorite_keys):
    if favorite_keys is None:
        return []
    if str(program_id) in favorite_keys:
        return [(kodiutils.get_string(32021),
                 "RunPlugin({})".format(plugin.url_for(favorite_remove, prog_id=program_id)))]
    return [(kodiutils.get_string(32020),
             "RunPlugin({})".format(plugin.url_for(favorite_add, prog_id=program_id, slug=slug)))]


@plugin.route('/account/favorites')
def favorites():
    try:
        entries = account.get_favorites()
    except LoginError:
        return session_expired()

    for favorite in entries:
        prog_id = str(favorite.get("key"))
        title = favorite.get("content_title", "")
        img = favorite.get("content_img", "")
        liz = ListItem(title)
        liz.setArt({"thumb": img,
                    "icon": img,
                    "fanart": kodiutils.FANART})
        liz.setInfo("Video", infoLabels={"title": title})
        liz.addContextMenuItems([(kodiutils.get_string(32021),
                                  "RunPlugin({})".format(plugin.url_for(favorite_remove, prog_id=prog_id)))])
        addDirectoryItem(
            plugin.handle,
            plugin.url_for(
                programs_episodes,
                title=title,
                img=img,
                prog_id=prog_id,
                page=1
            ), liz, True)
    endOfDirectory(plugin.handle)


@plugin.route('/account/favorites/add')
def favorite_add():
    favorite = rtpplay.get_program_favorite(plugin.args["prog_id"][0], plugin.args["slug"][0])
    if not favorite:
        return
    try:
        account.add_favorite(favorite)
    except LoginError:
        return kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32029))
    kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32030))
    xbmc.executebuiltin("Container.Refresh")


@plugin.route('/account/favorites/remove')
def favorite_remove():
    prog_id = plugin.args["prog_id"][0]
    try:
        for favorite in account.get_favorites():
            if str(favorite.get("key")) == prog_id:
                account.remove_favorite(favorite)
    except LoginError:
        return kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32029))
    kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32031))
    xbmc.executebuiltin("Container.Refresh")


@plugin.route('/account/watching')
def watching():
    try:
        entries = account.get_watching()
    except LoginError:
        return session_expired()

    for entry in entries:
        m = re.search(r"/play/p(\d+)/e(\d+)/([^/?#]*)", entry.get("content_url", ""))
        if not m:
            continue
        prog_id, episode_id, slug = m.groups()
        label = entry.get("content_title", "")
        if entry.get("content_episode"):
            label = "{} - Ep. {}".format(label, entry["content_episode"])
        if entry.get("content_date"):
            label = "{} ({})".format(label, "/".join(reversed(entry["content_date"].split("-"))))
        img = entry.get("content_img", "")

        liz = ListItem(label)
        liz.setArt({"thumb": img,
                    "icon": img,
                    "fanart": kodiutils.FANART})
        liz.setInfo("Video", infoLabels={"title": label})
        liz.setProperty('IsPlayable', 'true')
        # Shows the watched progress bar on the item
        liz.setProperty('ResumeTime', str(int(float(entry.get("progress") or 0)) // 1000))
        liz.setProperty('TotalTime', str(entry.get("content_duration") or 0))
        liz.addContextMenuItems([(kodiutils.get_string(32022),
                                  "RunPlugin({})".format(plugin.url_for(watching_remove, key=entry.get("key"))))])
        addDirectoryItem(
            plugin.handle,
            plugin.url_for(
                programs_play,
                title=label,
                img=img,
                episode_id=episode_id,
                prog_id=prog_id,
                slug=slug,
                resume=1
            ), liz, False)
    endOfDirectory(plugin.handle)


@plugin.route('/account/watching/remove')
def watching_remove():
    key = plugin.args["key"][0]
    try:
        for entry in account.get_watching():
            if str(entry.get("key")) == key:
                account.ended_watching(entry)
    except LoginError:
        return kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32029))
    xbmc.executebuiltin("Container.Refresh")


def play(liz, stream):
    if not stream:
        kodiutils.notification(kodiutils.get_string(32000), kodiutils.get_string(32002))
        setResolvedUrl(plugin.handle, False, liz)
        return

    liz.setProperty('IsPlayable', 'true')
    headers = urlencode(rtpplay.HEADERS)

    # DASH is only used for DRM content and always needs inputstream.adaptive
    use_isa = stream.manifest == "mpd" or (
        stream.manifest == "hls" and stream.media_type == "video" and kodiutils.get_setting_as_bool("use_isa"))
    if not use_isa:
        liz.setPath("{}|{}".format(stream.url, headers))
        setResolvedUrl(plugin.handle, True, liz)
        return

    is_helper = Helper(stream.manifest, drm="com.widevine.alpha" if stream.drm else None)
    if not is_helper.check_inputstream():
        setResolvedUrl(plugin.handle, False, liz)
        return

    liz.setPath(stream.url)
    liz.setContentLookup(False)
    if stream.manifest == "mpd":
        liz.setMimeType("application/dash+xml")
    liz.setProperty('inputstream', is_helper.inputstream_addon)
    if KODI_VERSION < 21:
        # Detected automatically (and deprecated) from Kodi 21 on
        liz.setProperty('inputstream.adaptive.manifest_type', stream.manifest)
    liz.setProperty('inputstream.adaptive.manifest_headers', headers)
    liz.setProperty('inputstream.adaptive.stream_headers', headers)
    if stream.drm:
        if KODI_VERSION >= 22:
            # license_type/license_key are deprecated from inputstream.adaptive 22.2
            liz.setProperty('inputstream.adaptive.drm_legacy', rtpplay.widevine_drm_legacy())
        else:
            liz.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            liz.setProperty('inputstream.adaptive.license_key', rtpplay.widevine_license_key())
    setResolvedUrl(plugin.handle, True, liz)


def run():
    plugin.run()
