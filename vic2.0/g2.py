from wxbot import *
import ConfigParser
import json

class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

    def tuling_auto_reply(self, uid, msg):
    	print self.get_head_img