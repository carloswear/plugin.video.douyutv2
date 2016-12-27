# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import os
import threading
import logging

#Initialize logging
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='[%(module)s][%(funcName)s] %(message)s')

WINDOW_FULLSCREEN_VIDEO = 12005
class TimeoutLabel(object):
    def __init__(self, label, timeout):
        self.label = label
        self.timeout = timeout


class BulletScreen(object):
    def __init__(self,  *args, **kwargs):
        self.window = xbmcgui.Window(WINDOW_FULLSCREEN_VIDEO)
        viewport_w, viewport_h = self._get_skin_resolution()
        self.running = False
        self.thread = threading.Thread(target = self.run)
        self.danmu = []
        self.labels = []
        self.lines = kwargs.get("lines", 3)
        self.textColor = kwargs.get("textColor", "0xFFFFFFFF")
        fontSize = kwargs.get("fontSize", "normal")
        position = kwargs.get("position", "up")
        self.left = 0
        self.width = int(viewport_w)
        self.speed = 5000
        if position == "up":
            self.top = int(viewport_h * 0.05)
        else:
            self.top = int(viewport_h * 0.75)
        self.height = int(viewport_h * 0.20)
        if fontSize == "normal":
            self.fontSize = "font15"
        else: 
            self.fontSize = "font16"

    def run(self):
        interval = 1000
        while self.running:
            for label in self.labels:
                if label.timeout < interval:
                    logging.info('Remove text: ' + label.label.getLabel())
                    self.window.removeControl(label.label)
                    self.labels.remove(label)
                else:
                    label.timeout -= interval
            xbmc.sleep(interval)

        logging.info('BulletScreen thread exit')
        for label in  self.labels:
            self.window.removeControl(label.label)


    def addText(self, text):
        if self.running == False:
            self.running = True
            self.thread.start()

        label = xbmcgui.ControlLabel(self.left, self.top, self.width, self.height, text, self.fontSize, self.textColor)
        logging.info('Add text: ' + text)
        self.danmu.append(text) #pending
        self.labels.append(TimeoutLabel(label, self.speed)) 
        self.window.addControl(label)
        label.setAnimations([('conditional', 'condition=true effect=slide start=%d,0 end=%d,0 time=%d' % (self.width, -self.width, self.speed))])

    def exit(self):
        if self.running == True:
            self.running = False
            self.thread.join()


    # This is so hackish it hurts.
    def _get_skin_resolution(self):
        import xml.etree.ElementTree as ET
        skin_path = xbmc.translatePath("special://skin/")
        tree = ET.parse(os.path.join(skin_path, "addon.xml"))
        res = tree.findall("./extension/res")[0]
        return int(res.attrib["width"]), int(res.attrib["height"])


if __name__ == '__main__':
    import xbmcgui
    import xbmcplugin
    import sys
    from urlparse import parse_qsl
    from douyudanmu import douyudanmu
    if 0:
        from addon import router
        router(sys.argv[2][1:])
    else:
        __handle__ = int(sys.argv[1])
        params = dict(parse_qsl(sys.argv[2][1:]))
        if 'test' in params:
            xbmcplugin.setResolvedUrl(__handle__, True, xbmcgui.ListItem(path='d:\empty.mpeg'))
            player = xbmc.Player()
            bs = BulletScreen()
            danmu=douyudanmu('138286')
            while not player.isPlaying():
                xbmc.sleep(1000)
            while not xbmc.abortRequested and player.isPlaying():
                s=danmu.get_danmu()
                logging.info(s)
                if len(s)!=0:
                    bs.addText(s)
            bs.exit()
        else:
            item = xbmcgui.ListItem(label='Play')
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(__handle__, sys.argv[0]+'?test=1', item)
            xbmcplugin.endOfDirectory(__handle__) 
