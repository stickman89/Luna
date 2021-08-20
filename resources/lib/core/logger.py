import xbmc

class Logger:

    def info(self, text):
        xbmc.log(text, level=xbmc.LOGINFO)

    def debug(self, text):
        xbmc.log(text)

    def error(self, text):
        xbmc.log(text, level=xbmc.LOGERROR)
