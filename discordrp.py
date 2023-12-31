QL_DISCORD_RP_ID = '# discord_status: Set Discord status as current song.'

from senf import fsn2uri
from math import floor
from quodlibet import _, app
from quodlibet.plugins import PluginConfig, ConfProp
from quodlibet.plugins.events import EventPlugin
from quodlibet.pattern import Pattern
from gi.repository import Gtk
from time import time
from quodlibet.qltk.tracker import TimeTracker
from urllib.parse import unquote, urlparse
import asyncio
try:
    from pypresence import Presence, InvalidID, DiscordNotFound
except ImportError:
    from quodlibet.plugins import MissingModulePluginException
    raise MissingModulePluginException("pypresence")

try:
    import requests
except ImportError:
    from quodlibet.plugins import MissingModulePluginException
    raise MissingModulePluginException("requests")    

try:
    from PIL import Image
except ImportError:
    from quodlibet.plugins import MissingModulePluginException
    raise MissingModulePluginException("pillow")   

# defaults
QL_DISCORD_RP_ID = '0'
CONFIG_DEFAULT_RP_LINE1 = "<title>"
CONFIG_DEFAULT_RP_LINE2 = "on <album> (by <artist>)"
DEF_PAUSE_IMAGE = "https://cdn-icons-png.flaticon.com/512/9974/9974128.png"
DEF_PLAY_IMAGE = "https://cdn-icons-png.flaticon.com/512/9974/9974140.png"
DEF_URL = "https://placekitten.com"
QL_LARGE_IMAGE = "https://cdn.discordapp.com/emojis/688028506252115999.gif"
DEF_LOADING_IMAGE = "https://media.tenor.com/wpSo-8CrXqUAAAAi/loading-loading-forever.gif"
class DiscordStatusConfig:
    _config = PluginConfig(__name__)

    rp_line1 = ConfProp(_config, "rp_line1", CONFIG_DEFAULT_RP_LINE1)
    rp_line2 = ConfProp(_config, "rp_line2", CONFIG_DEFAULT_RP_LINE2)
    rp_id = ConfProp(_config, "rp_id", QL_DISCORD_RP_ID)
    playimage = ConfProp(_config, "playimage", DEF_PLAY_IMAGE)
    pauseimage = ConfProp(_config, "pauseimage", DEF_PAUSE_IMAGE)
    buttonurl = ConfProp(_config, "buttonurl", DEF_URL)
    largeimage = ConfProp(_config, "largeimage", QL_LARGE_IMAGE)
    loadingimage = ConfProp(_config, "loadingimage", DEF_LOADING_IMAGE)


discord_status_config = DiscordStatusConfig()


class DiscordStatusMessage(EventPlugin):
    PLUGIN_ID = _("Discord-rp")
    PLUGIN_NAME = _("Discord Rich Presence")
    PLUGIN_DESC = _("Uses Discord Rich Presence (using pypresence) to show everyone what you're listening to")
    VERSION = "0.1"

    def __init__(self):
        self.song = None
        self.discordrp = None
        self._tracker = TimeTracker(app.player)
        self._tracker.connect('tick', self._on_tick, app.player)
        self.__image_fp = None
        self.albumurl = None
        self.albumname = None

    def _get_image_uri(self, song): # see https://github.com/quodlibet/quodlibet/blob/main/quodlibet/ext/events/notify.py#L330
        fileobj = app.cover_manager.get_cover(song)
        if self.__image_fp is not None:
            self.__image_fp.close()
            self.__image_fp = None
        self.__image_fp = fileobj
        if fileobj:
            return fsn2uri(fileobj.name)
        return u""

    def length(self, string):
        while len(string) < 2: string += "."
        if len(string) > 32: string = string[0:29] + "..."
        return string

    def uploadtocatbox(self, uri):
        loop = asyncio.get_event_loop()
        img = Image.open(unquote(urlparse(uri).path)); img = img.convert('RGB')
        img = img.resize((60, 60)) # 60x60 might seem low but it's the size of the large image preview
        img.save('/tmp/quodlibet-albumart.jpg', optimize=True, quality=75)
        try:
            return requests.post("https://litterbox.catbox.moe/resources/internals/api.php", timeout=10,
                    data={"reqtype": "fileupload", "time": "1h"}, files={"fileToUpload": open("/tmp/quodlibet-albumart.jpg", "rb")}).text
        except: pass
        return discord_status_config.largeimage

    def createbar(self):
        bar = "["
        percentage = (app.player.get_position() // 1000) / app.player.info("~#length")
        boldbars = floor(28 * percentage)
        for _ in range(boldbars): bar += "━"
        if len(bar) >= 28: # if already full (as backup)
            bar = bar[:-1] + "⬤"
        else:
            bar += "⬤"
            for _ in range(26 - boldbars): bar += "─"
        bar += "]"
        return bar

    def update_discordrp(self, details, state=None):
        if not self.discordrp:
            try:
                self.discordrp = Presence(discord_status_config.rp_id, pipe=0)
                self.discordrp.connect()
            except (DiscordNotFound, ConnectionRefusedError):
                self.discordrp = None

        if self.discordrp:
            try:
                if app.player.paused: self.discordrp.update(details=self.length(details), state=self.length(state), 
                                                            large_image=self.albumurl, small_image=discord_status_config.pauseimage, large_text=self.albumname, small_text="Paused",
                                                            buttons=[{"label": "PAUSED", "url": discord_status_config.buttonurl}])
                else:                 self.discordrp.update(details=self.length(details), state=self.length(state), 
                                                            large_image=self.albumurl, small_image=discord_status_config.playimage, end=self.epoch_time, large_text=self.albumname, small_text="Playing",
                                                            buttons=[{"label": self.createbar(), "url": discord_status_config.buttonurl}])
            except InvalidID:
                self.discordrp = None

    def handle_play(self):
        try: self.remainingtime = app.player.info("~#length") - app.player.get_position() // 1000
        except: # will fail if nothing playing
            self.remainingtime = 0
        self.epoch_time = int(time() + self.remainingtime)
        if self.song:
            details = Pattern(discord_status_config.rp_line1) % self.song
            state = Pattern(discord_status_config.rp_line2) % self.song

            while len(details) < 2: details += " "
            while len(state) < 2: state += " "

            self.update_discordrp(details, state)

    def plugin_on_seek(self, _, __):
        self.handle_play()

    def plugin_on_song_started(self, song):
        self.updatestuff(song)
        

    def updatestuff(self, song):
        self.song = song
        if self.albumname != Pattern("<album>") % self.song or self.albumurl == discord_status_config.largeimage:
            self.albumurl = discord_status_config.loadingimage
            self.handle_play() # update first with loading gif
            self.albumurl = self.uploadtocatbox(self._get_image_uri(self.song))
            self.albumname = Pattern("<album>") % self.song
        self.handle_play()

    def plugin_on_paused(self):
        self.handle_play()

    def plugin_on_unpaused(self): 
        self.handle_play()
    
    def _on_tick(self, _, __): # every second when music is playing
        self.handle_play()
    
    def disabled(self):
        if self.discordrp:
            self.discordrp.clear()
            self.discordrp.close()
            self.discordrp = None
            self.song = None

    def PluginPreferences(self, parent):
        vb = Gtk.VBox(spacing=6)

        def rp_line1_changed(entry):
            discord_status_config.rp_line1 = entry.get_text()
        def rp_line2_changed(entry):
            discord_status_config.rp_line2 = entry.get_text()
        def rp_id_changed(entry):
            discord_status_config.rp_id = entry.get_text()
        def playimage_changed(entry):
            discord_status_config.playimage = entry.get_text()
        def pauseimage_changed(entry):
            discord_status_config.pauseimage = entry.get_text()
        def buttonurl_changed(entry):
            discord_status_config.buttonurl = entry.get_text()
        def largeimage_changed(entry):
            discord_status_config.largeimage = entry.get_text()
        def loadingimage_changed(entry):
            discord_status_config.loadingimage = entry.get_text()

        # TODO: rewrite using defs
        status_line1_box = Gtk.HBox(spacing=6)
        status_line1_box.set_border_width(3)
        status_line1 = Gtk.Entry()
        status_line1.set_text(discord_status_config.rp_line1)
        status_line1.connect('changed', rp_line1_changed)
        status_line1_box.pack_start(Gtk.Label(label=_("Status Line #1")), False, True, 0)
        status_line1_box.pack_start(status_line1, True, True, 0)

        status_line2_box = Gtk.HBox(spacing=3)
        status_line2_box.set_border_width(3)
        status_line2 = Gtk.Entry()
        status_line2.set_text(discord_status_config.rp_line2)
        status_line2.connect('changed', rp_line2_changed)
        status_line2_box.pack_start(Gtk.Label(label=_('Status Line #2')), False, True, 0)
        status_line2_box.pack_start(status_line2, True, True, 0)

        rp_id_config_box = Gtk.HBox(spacing=3)
        rp_id_config_box.set_border_width(3)
        rp_id_config = Gtk.Entry()
        rp_id_config.set_text(discord_status_config.rp_id)
        rp_id_config.connect('changed', rp_id_changed)
        rp_id_config_box.pack_start(Gtk.Label(label=_('App ID')), False, True, 0)
        rp_id_config_box.pack_start(rp_id_config, True, True, 0)

        playimage_config_box = Gtk.HBox(spacing=3)
        playimage_config_box.set_border_width(3)
        playimage_config = Gtk.Entry()
        playimage_config.set_text(discord_status_config.playimage)
        playimage_config.connect('changed', playimage_changed)
        playimage_config_box.pack_start(Gtk.Label(label=_('Play image ')), False, True, 0)
        playimage_config_box.pack_start(playimage_config, True, True, 0)

        pauseimage_config_box = Gtk.HBox(spacing=3)
        pauseimage_config_box.set_border_width(3)
        pauseimage_config = Gtk.Entry()
        pauseimage_config.set_text(discord_status_config.pauseimage)
        pauseimage_config.connect('changed', pauseimage_changed)
        pauseimage_config_box.pack_start(Gtk.Label(label=_('Pause image')), False, True, 0)
        pauseimage_config_box.pack_start(pauseimage_config, True, True, 0)

        buttonurl_config_box = Gtk.HBox(spacing=3)
        buttonurl_config_box.set_border_width(3)
        buttonurl_config = Gtk.Entry()
        buttonurl_config.set_text(discord_status_config.buttonurl)
        buttonurl_config.connect('changed', buttonurl_changed)
        buttonurl_config_box.pack_start(Gtk.Label(label=_('Button URL')), False, True, 0)
        buttonurl_config_box.pack_start(buttonurl_config, True, True, 0)

        largeimage_config_box = Gtk.HBox(spacing=3)
        largeimage_config_box.set_border_width(3)
        largeimage_config = Gtk.Entry()
        largeimage_config.set_text(discord_status_config.largeimage)
        largeimage_config.connect('changed', largeimage_changed)
        largeimage_config_box.pack_start(Gtk.Label(label=_('Fallback album art')), False, True, 0)
        largeimage_config_box.pack_start(largeimage_config, True, True, 0)

        loadingimage_config_box = Gtk.HBox(spacing=3)
        loadingimage_config_box.set_border_width(3)
        loadingimage_config = Gtk.Entry()
        loadingimage_config.set_text(discord_status_config.loadingimage)
        loadingimage_config.connect('changed', loadingimage_changed)
        loadingimage_config_box.pack_start(Gtk.Label(label=_('Loading image')), False, True, 0)
        loadingimage_config_box.pack_start(loadingimage_config, True, True, 0)

        vb.pack_start(status_line1_box, True, True, 0)
        vb.pack_start(status_line2_box, True, True, 0)
        vb.pack_start(rp_id_config_box, True, True, 0)
        vb.pack_start(playimage_config_box, True, True, 0)
        vb.pack_start(pauseimage_config_box, True, True, 0)
        vb.pack_start(buttonurl_config_box, True, True, 0)
        vb.pack_start(largeimage_config_box, True, True, 0)
        vb.pack_start(loadingimage_config_box, True, True, 0)

        return vb

