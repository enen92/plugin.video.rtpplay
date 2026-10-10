import xbmcaddon
import xbmcgui
import xbmcvfs
import logging

# read settings
ADDON = xbmcaddon.Addon()

ICON = xbmcvfs.translatePath(ADDON.getAddonInfo("icon"))
FANART = xbmcvfs.translatePath(ADDON.getAddonInfo("fanart"))
PROFILE = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
logger = logging.getLogger(__name__)


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
    return str(ADDON.getLocalizedString(string_id))

