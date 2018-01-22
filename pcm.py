#!/usr/bin/python  
#-*-coding:utf-8-*- 

import win32com.client
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import mp3play

filename = r'F:\2017-5-6\1111.mp3'    
mp3 = mp3play.load(filename)    
mp3.play()    
import time    
time.sleep(min(10, mp3.seconds()))    
mp3.stop()
