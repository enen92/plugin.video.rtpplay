# -*- coding: utf-8 -*-
import os

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import sys
import logging
import json as json
import re
import base64

PY3 =  sys.version_info > (3, 0)

if PY3:
    from urllib.request import urlopen
    from urllib.parse import unquote
    from html.parser import HTMLParser
else:
    from urllib2 import urlopen
    from urlparse import unquote
    from HTMLParser import HTMLParser

# read settings
ADDON = xbmcaddon.Addon()


if PY3:
    ICON = xbmcvfs.translatePath(ADDON.getAddonInfo("icon"))
    FANART = xbmcvfs.translatePath(ADDON.getAddonInfo("fanart"))
    PROFILE = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
else:
    ICON = xbmc.translatePath(ADDON.getAddonInfo("icon"))
    FANART = xbmc.translatePath(ADDON.getAddonInfo("fanart"))
    PROFILE = xbmc.translatePath(ADDON.getAddonInfo('profile'))

TEMP = os.path.join(PROFILE, 'temp', '')
logger = logging.getLogger(__name__)


class HTMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        if PY3:
            self.strict = False
            self.convert_charrefs = True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_html_tags(html):
    s = HTMLStripper()
    s.feed(html)
    return s.get_data()

def compat_py23str(x):
    if PY3:
        return str(x)
    else:
        if isinstance(x, unicode):
            try:
                return unicode(x).encode("utf-8")
            except UnicodeEncodeError:
                try:
                    return unicode(x).encode("utf-8")
                except:
                   return str(x)
        else:
            return str(x)


def ok(heading, line1, line2="", line3=""):
    xbmcgui.Dialog().ok(heading, line1, line2, line3)


def notification(header, message, time=5000, icon=ADDON.getAddonInfo('icon'), sound=True):
    xbmcgui.Dialog().notification(header, message, icon, time, sound)


def show_settings():
    ADDON.openSettings()


def get_setting(setting):
    return ADDON.getSetting(setting).strip()

def set_setting(setting, value):
    ADDON.setSetting(setting, str(value))


def get_setting_as_bool(setting):
    return get_setting(setting).lower() == "true"


def get_setting_as_float(setting):
    try:
        return float(get_setting(setting))
    except ValueError:
        return 0


def get_setting_as_int(setting):
    try:
        return int(get_setting_as_float(setting))
    except ValueError:
        return 0


def get_string(string_id):
    return compat_py23str(ADDON.getLocalizedString(string_id))


def kodi_json_request(params):
    data = json.dumps(params)
    request = xbmc.executeJSONRPC(data)

    try:
        response = json.loads(request)
    except UnicodeDecodeError:
        response = json.loads(request.decode('utf-8', 'ignore'))

    try:
        if 'result' in response:
            return response['result']
        return None
    except KeyError:
        logger.warn("[%s] %s" %
                    (params['method'], response['error']['message']))
        return None


def find_stream_url(html):
    url = ''

    needle = [  "hls : atob( decodeURIComponent(",
                "hls : ",
                '.mp3',
                "hls : atob(decodeURIComponent("]

    if needle[0] in html:
        # Testado com:
        # https://www.rtp.pt/play/p3909/e308024/4play
        # https://www.rtp.pt/play/p8632/kubrick-na-voz-de-kubrick
        ini = html.find(needle[0]) + len(needle[0])     # Procura atob
        url = html[ini:]                                # Obtém o resto do HTML
        end = url.find("]") - 1                         # Procura o fim do array ]
        url = url[:end]                                 # Obtém o array de strings
        url = unquote(url.replace('["','').replace('","','').replace('"].join(""))) },',''))    # Remove aspas, vírgulas e parte final do JS
        url = base64.b64decode(url).decode('utf-8')     # Descodifica URL
    elif needle[3] in html:
        # Testado com:
        # https://www.rtp.pt/play/estudoemcasa/p7776/portugues-1-ano
        ini = html.find(needle[3]) + len(needle[3])     # Procura atob
        url = html[ini:]                                # Obtém o resto do HTML
        end = url.find("]") - 1                         # Procura o fim do array ]
        url = url[:end]                                 # Obtém o array de strings
        url = unquote(url.replace('["','').replace('","','').replace('"].join(""))) },',''))    # Remove aspas, vírgulas e parte final do JS
        url = base64.b64decode(url).decode('utf-8')     # Descodifica URL
    elif needle[1] in html:
        # Testado com:
        # https://www.rtp.pt/play/palco/p7732/electrico
        ini = html.find(needle[1]) + len(needle[1]) +1  # Procura hls : 
        url = html[ini:]                                # Obtém resto do HTML
        end = url.find('",')                            # Procura o fim do atributo ",
        url = url[:end]                                 # Obtém o URL
    elif needle[2] in html:
        # Testado com:
        # https://www.rtp.pt/play/p8695/flawless-radio
        end = html.find(needle[2]) + len(needle[2]) # Procura por .mp3
        url = html[:end]                            # Obtém HTML até ao .mp3
        ini = url.rfind('"') + 1                    # Procura a primeira " a partir da direita
        url = url[ini:]                             # Obtém o URL

    url = url.replace('cdn-ondemand','streaming-ondemand')          # Altera servidor
    url = url.replace('streaming-ondemand','ondemand-streaming')    # Altera servidor

    if url.endswith("/master.m3u8"):                                # Corrige extensão para .mp4
        url = url.replace("/master.m3u8",".mp4")

    return url

    raise ValueError


def convertVttSrt(fileContents):
    # taken from https://github.com/jansenicus/vtt-to-srt.py/blob/master/vtt_to_srt.py#L29
    replacement = re.sub(r'(\d\d:\d\d:\d\d).(\d\d\d) --> (\d\d:\d\d:\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n',
                         r'\1,\2 --> \3,\4\n', fileContents)
    replacement = re.sub(r'(\d\d:\d\d).(\d\d\d) --> (\d\d:\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n',
                         r'\1,\2 --> \3,\4\n', replacement)
    replacement = re.sub(r'(\d\d).(\d\d\d) --> (\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n', r'\1,\2 --> \3,\4\n',
                         replacement)
    replacement = re.sub(r'WEBVTT\n', '', replacement)
    replacement = re.sub(r'Kind:[ \-\w]+\n', '', replacement)
    replacement = re.sub(r'Language:[ \-\w]+\n', '', replacement)
    replacement = re.sub(r'<c[.\w\d]*>', '', replacement)
    replacement = re.sub(r'</c>', '', replacement)
    replacement = re.sub(r'<\d\d:\d\d:\d\d.\d\d\d>', '', replacement)
    replacement = re.sub(r'::[\-\w]+\([\-.\w\d]+\)[ ]*{[.,:;\(\) \-\w\d]+\n }\n', '', replacement)
    replacement = re.sub(r'Style:\n##\n', '', replacement)
    return replacement


def find_subtitles(html):
    try:
        match = re.search(r'["\']\s*?http(.*?)\.vtt\s*?["\']', html)
        if match and len(match.groups()) > 0:
            url = "http" + match.group(1) + ".vtt"
            last_slash = url.rfind("/")
            if last_slash != -1:
                id = url[last_slash + 1:len(url) - 4]
                if not os.path.exists(TEMP):
                    os.makedirs(TEMP)
                file = os.path.join(TEMP, "{id}.srt".format(id=id))
                response = urlopen(url)
                with open(file, "w") as local_file:
                    local_file.write(convertVttSrt(response.read().decode('utf-8')))
                return file
    except Exception:
        pass
