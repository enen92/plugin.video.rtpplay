"""
    Reports playback progress of RTP Play episodes to the user's RTP account,
    so "Continue watching" stays in sync with the website and apps.

    The plugin hands over the episode in a window property just before it
    resolves the stream; this service picks it up once that stream starts.
"""

import json
import logging
import time

import xbmc
import xbmcaddon
import xbmcgui

from resources.lib import kodilogging, kodiutils
from resources.lib.rtpaccount import Account

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
PLAYBACK_PROPERTY = "plugin.video.rtpplay.playback"

# Same thresholds as the website: nothing is saved for the first 30 seconds,
# and the last 30 seconds count as having finished the episode
MIN_PROGRESS_S = 30
END_MARGIN_S = 30
HEARTBEAT_S = 30


class Player(xbmc.Player):
    def __init__(self):
        super().__init__()
        self.session = None

    def onAVStarted(self):
        self.finish()
        window = xbmcgui.Window(10000)
        data = window.getProperty(PLAYBACK_PROPERTY)
        if not data:
            return
        data = json.loads(data)
        try:
            playing = self.getPlayingFile()
        except RuntimeError:
            return
        if not playing.split("|")[0].startswith(data["url"].split("|")[0]):
            # Something else started playing
            return
        window.clearProperty(PLAYBACK_PROPERTY)
        self.session = {"telemetry": data["telemetry"], "position": 0.0, "total": 0.0, "reported": 0.0}
        if data.get("resume_ms"):
            self.seekTime(data["resume_ms"] / 1000.0)

    def onPlayBackStopped(self):
        self.finish()

    def onPlayBackEnded(self):
        if self.session:
            self.session["position"] = self.session["total"]
        self.finish()

    def onPlayBackError(self):
        self.session = None

    def tick(self):
        if not self.session or not self.isPlaying():
            return
        try:
            self.session["position"] = self.getTime()
            self.session["total"] = self.getTotalTime()
        except RuntimeError:
            return
        if time.time() - self.session["reported"] >= HEARTBEAT_S:
            self.report(final=False)

    def finish(self):
        if self.session:
            self.report(final=True)
        self.session = None

    def report(self, final):
        session = self.session
        session["reported"] = time.time()
        position, total = session["position"], session["total"]
        account = Account(kodiutils.PROFILE)
        if not account.logged_in:
            return
        try:
            if total and total - position <= END_MARGIN_S:
                if final:
                    account.ended_watching(session["telemetry"])
            elif position >= MIN_PROGRESS_S:
                account.update_watching(session["telemetry"], int(position * 1000))
        except Exception:
            logger.exception("Could not update continue watching")


def run():
    kodilogging.config()
    monitor = xbmc.Monitor()
    player = Player()
    while not monitor.waitForAbort(1):
        player.tick()
    player.finish()
