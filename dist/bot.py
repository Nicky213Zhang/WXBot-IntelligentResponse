#!/usr/bin/env python
# coding: utf-8
# 

from wxbot import *
import ConfigParser
import json
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = ""
        self.robot_switch = True

        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print 'tuling_key:', self.tuling_key

    def tuling_auto_reply(self, uid, msg):
        db = MySQLdb.connect(host='127.0.0.1', passwd='gjc806626',user='root',db='vicwxk',charset='utf8')
      
        cursor = db.cursor()
        msgtext = msg.encode('utf8')
        cursor.execute("select * from vic_codetext where keyword like '%%%%%s%%%%'"%msgtext)
        values = cursor.fetchall()
        cursor.close()
        db.close()
        if values == ():
            if self.tuling_key:
                url = "http://www.tuling123.com/openapi/api"
                user_id = uid.replace('@', '')[:30]
                body = {'key': self.tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
                r = requests.post(url, data=body)
                respond = json.loads(r.text)
                result = ''
                if respond['code'] == 100000:
                    result = respond['text'].replace('<br>', '  ')
                    result = result.replace(u'\xa0', u' ')
                elif respond['code'] == 200000:
                    result = respond['url']
                elif respond['code'] == 302000:
                    for k in respond['list']:
                        result = result + u"【" + k['source'] + u"】 " +\
                        k['article'] + "\t" + k['detailurl'] + "\n"
                else:
                    result = respond['text'].replace('<br>', '  ')
                    result = result.replace(u'\xa0', u' ')
                print '    ROBOT:', result
                jsonData = []
                res = {}
                res['keyword'] = result
                res['type']    = 'text'
                jsonData.append(res)
                jsondatar = json.dumps(jsonData, ensure_ascii=False)
                code = jsondatar[1:len(jsondatar)-1]
                respond = json.loads(code)
                return respond
                #return result
            else:
                return u"知道啦"
        else:
            jsonData = []
            for row in values:
                result = {}
                result['text']    = row[0]
                result['id']      = row[1]
                result['keyword'] = str(row[2])
                result['datatime']= str(row[3])
                result['type']    = str(row[4])
                jsonData.append(result)
            jsondatar=json.dumps(jsonData,ensure_ascii=False)
            code = jsondatar[1:len(jsondatar)-1]
            respond = json.loads(code)
            #result = respond['keyword']
            return respond
        
    def auto_switch(self, msg):
        msg_data = msg['content']['data']
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开']
        start_cmd = [u'出来', u'启动', u'工作']
        if self.robot_switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已关闭！', msg['to_user_id'])
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已开启！', msg['to_user_id'])

    def handle_msg_all(self, msg):
        if not self.robot_switch and msg['msg_type_id'] != 1:
            return
        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:  # reply to self
            print 'bbb'
            self.auto_switch(msg)
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 0:  # text message from contact
            nick = msg['user']['name']
            uidd = msg['user']['id']
            self.get_head_img(uidd, nick)
            msg_ty = self.tuling_auto_reply(msg['user']['id'], msg['content']['data'])
            if msg_ty['type'] == 'img':
                img = self.temp_pwd + '/images/img_' + msg_ty['keyword'] + '.jpg'
                self.send_img_msg_by_uid(img, msg['user']['id'])
                self.send_msg_by_uid('[偷笑]', msg['user']['id'])
            elif msg_ty['type'] == 'voice':
                voice = self.temp_pwd + '/voice/voice_' + msg_ty['keyword'] + '.mp3'
                self.send_file_msg_by_uid(voice, msg['user']['id'])
            elif msg_ty['type'] == 'video':
                video = self.temp_pwd + '/video/video_' + msg_ty['keyword'] + '.mp4'
                self.send_file_msg_by_uid(video, msg['user']['id'])
            elif msg_ty['type'] == 'text':
                self.send_msg_by_uid(msg_ty['keyword'], msg['user']['id'])
        elif msg['msg_type_id'] == 3 and msg['content']['type'] == 0:  # group text message
            nick = msg['user']['name']
            uidd = msg['user']['id']
            gid = msg['content']['user']['id']
            name = msg['content']['user']
            self.get_head_img(uidd, nick)
            self.get_icon(gid, uidd, name)
            if 'detail' in msg['content']:
                my_names = self.get_group_member_name(msg['user']['id'], self.my_account['UserName'])
                if my_names is None:
                    my_names = {}
                if 'NickName' in self.my_account and self.my_account['NickName']:
                    my_names['nickname2'] = self.my_account['NickName']
                if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                    my_names['remark_name2'] = self.my_account['RemarkName']

                is_at_me = False
                for detail in msg['content']['detail']:
                    if detail['type'] == 'at':
                        for k in my_names:
                            if my_names[k] and my_names[k] == detail['value']:
                                is_at_me = True
                                break
                if is_at_me:
                    src_name = msg['content']['user']['name']
                    if src_name == 'unknown':
                        reply = ''
                    else:
                        reply = '@' + src_name + ' '
                    if msg['content']['type'] == 0:  # text message
                        msg_content = msg['content']
                        reply_key = self.tuling_auto_reply(msg_content['user']['id'], msg_content['desc'])
                        res_turn = reply + reply_key['keyword']
                    else:
                        reply += u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                    self.send_msg_by_uid(res_turn, msg['user']['id'])


def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'

    bot.run()


if __name__ == '__main__':
    main()

