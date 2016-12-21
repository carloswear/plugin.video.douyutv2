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
VIEWPORT_WIDTH = 1920.0
VIEWPORT_HEIGHT = 1080.0
class OverlayText(object):
    def __init__(self,  *args, **kwargs):
        self.window = xbmcgui.Window(WINDOW_FULLSCREEN_VIDEO)
        viewport_w, viewport_h = self._get_skin_resolution()
        # Adjust size based on viewport, we are using 1080p coordinates
        self._shown = False
        self.danmu = []
        self.textlist = []
        self.emptylines = []
        self.thread = threading.Thread(target=self.scroll)
        self.running = True
        self.lines = kwargs.get("lines", 3)
        textColor = kwargs.get("textColor", "0xFFFFFFFF")
        fontSize = kwargs.get("fontSize", "normal")
        position = kwargs.get("position", "up")
        left = -viewport_w*0.55
        width = viewport_w*1.55
        if position == "up":
            top = viewport_h * 0.05
        else:
            top = viewport_h * 0.75
        height = viewport_h * 0.20
        if fontSize == "normal":
            fontSize = "font15"
            self.char_per_line = 240
        else: 
            fontSize = "font16"
            self.char_per_line = 180
        for i in  range(self.lines):
            text = ''
            for j in range(self.char_per_line):
                text += ' ' 
            self.textlist.append(text)
            self.emptylines.append(i)

        self._label = xbmcgui.ControlLabel(int(left), int(top), int(width), int(height),
                                           "", fontSize, textColor, alignment=1)

    def scroll(self):
        speed = 1
        while self.running:
            if not self._shown:
                time.sleep(0.1)
                continue

            for l in self.emptylines:
                for i in range(speed):
                    self.textlist[l] += ' '
                    while (self.strlen(self.textlist[l]) > self.char_per_line):
                        self.textlist[l] = self.textlist[l][1:]

            for i in range(self.lines):
                if len(self.danmu) <= i:
                    #No more danmu
                    break
                
                if self.danmu[i][1] == -1:
                    if len(self.emptylines) == 0:
                        #Corrupt
                        logging.error('No empty lines')
                        break
                    self.danmu[i] = (self.danmu[i][0], self.emptylines[0])
                    line = self.emptylines.pop(0)
                    logging.debug('LINE:'+str(line)+':')
                    logging.debug(self.emptylines)
                    logging.debug(self.danmu[:3])

                danmu = self.danmu[i]
                line = danmu[1]
                self.textlist[line] += danmu[0][:speed]
                while (self.strlen(self.textlist[line]) > self.char_per_line):
                    self.textlist[line] = self.textlist[line][1:]
                self.danmu[i] = (danmu[0][speed:], danmu[1])
                if len(self.danmu[i][0]) == 0:
                    #This danmu is empty
                    self.emptylines.append(danmu[1])
                    logging.debug(str(danmu[1])+' FREE')
                    logging.debug(self.emptylines)
                    logging.debug(self.danmu[:3])
                    self.danmu.pop(i)

            #Update text. 
            self.update()
            time.sleep(0.1)
        logging.info('Danmu exit')

    def strlen(self, text):
        length = len(text)
        utf8_length = len(text.encode('utf-8'))
        return (utf8_length - length) / 2 + length

    def show(self):
        if not self._shown:
            self.window.addControls([self._label])
            self._shown = True
            self.thread.start()

    def hide(self):
        if self._shown:
            self._shown = False
            self.window.removeControls([ self._label])
            self.running = False

    def close(self):
        self.hide()

    def add(self, text):
        text += ' '
        logging.debug('TEXT:' + text)
        self.danmu.append((text, -1)) #pending

    def update(self):
        text = u'\n'.join(self.textlist)
        self._label.setLabel(text)

    # This is so hackish it hurts.
    def _get_skin_resolution(self):
        import xml.etree.ElementTree as ET
        skin_path = xbmc.translatePath("special://skin/")
        tree = ET.parse(os.path.join(skin_path, "addon.xml"))
        res = tree.findall("./extension/res")[0]
        return int(res.attrib["width"]), int(res.attrib["height"])
