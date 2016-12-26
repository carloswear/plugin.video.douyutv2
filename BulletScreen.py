#adopted from https://github.com/steeve/xbmctorrent/blob/master/resources/site-packages/xbmctorrent/player.py
import xbmc
import xbmcaddon
import xbmcgui
import os
import threading
import time
import logging

#Initialize logging
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='[%(levelname)s][%(funcName)s] %(message)s')

WINDOW_FULLSCREEN_VIDEO = 12005
class BulletScreen(object):
    def __init__(self,  *args, **kwargs):
        self.window = xbmcgui.Window(WINDOW_FULLSCREEN_VIDEO)
        viewport_w, viewport_h = self._get_skin_resolution()
        self.danmu = []
        self.labels = []
        self.lines = kwargs.get("lines", 3)
        self.textColor = kwargs.get("textColor", "0xFFFFFFFF")
        fontSize = kwargs.get("fontSize", "normal")
        position = kwargs.get("position", "up")
        self.left = viewport_w
        self.width = viewport_w
        self.speed = 5000
        if position == "up":
            self.top = viewport_h * 0.05
        else:
            self.top = viewport_h * 0.75
        self.height = viewport_h * 0.20
        if fontSize == "normal":
            self.fontSize = "font15"
        else: 
            self.fontSize = "font16"

    def add(self, text):
        label = xbmcgui.ControlLabel(self.left, self.top, self.width, self.height, text, self.fontSize, self.textColor)
        logging.debug('TEXT:' + text)
        self.danmu.append(text) #pending
        self.labels.append(text) 
        self.window.addControl(label)
        label.setAnimations([('conditional', 'condition=true effect=slide start=%d,0 end=%d,0 time=%d' % (self.width, self.width, self.speed))])


    # This is so hackish it hurts.
    def _get_skin_resolution(self):
        import xml.etree.ElementTree as ET
        skin_path = xbmc.translatePath("special://skin/")
        tree = ET.parse(os.path.join(skin_path, "addon.xml"))
        res = tree.findall("./extension/res")[0]
        return int(res.attrib["width"]), int(res.attrib["height"])
