# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import re
import os
import urllib2,json
from lxml import etree

HELP_INFO = \
u"""
欢迎关注我们^_^
微信在线听歌,发送歌曲名将会收听到该歌曲。
"""

MSG_NEWS_HEADER= \
u"""
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<Content><![CDATA[]]></Content>
<ArticleCount>%d</ArticleCount>
<Articles>
"""
MSG_NEWS_TAIL= \
u"""
</Articles>
<FuncFlag>1</FuncFlag>
</xml>
"""
MSG_PIC= \
u"""
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%d</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>1</ArticleCount>
<Articles>
<item>
<Title><![CDATA[%s]]></Title>
<Description><![CDATA[%s]]></Description>
<PicUrl><![CDATA[%s]]></PicUrl>
<Url><![CDATA[%s]]></Url>
</item>
</Articles>
<FuncFlag>1</FuncFlag>
</xml>
"""
MSG_TEXT= \
u"""
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%d</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>
"""
MSG_MUSIC= \
u"""
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%d</CreateTime>
<MsgType><![CDATA[music]]></MsgType>
<Music>
<Title><![CDATA[%s]]></Title>
<Description><![CDATA[%s]]></Description>
<MusicUrl><![CDATA[%s]]></MusicUrl>
<HQMusicUrl><![CDATA[%s]]></HQMusicUrl>
</Music>
<FuncFlag>0</FuncFlag>
</xml>
"""
#Subscribe decision
def user_subscribe_event(msg):
    return msg['MsgType'] == 'event' and msg['Event'] == 'subscribe'

def response_text_msg(fromuser, touser, content):
    s = MSG_TEXT % (fromuser, touser, int(time.time()), content)
    return s 
def response_music_msg(fromuser, touser, title, description, url, hqurl):
    s = MSG_MUSIC % (fromuser, touser, int(time.time()), title, description, url, hqurl)
    return s 
def response_news_msg(fromuser, touser, title, description, picurl, url):
    s = MSG_PIC % (fromuser, touser, int(time.time()), title, description, picurl, url)
    return s 
class WeixinInterface:
    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)
 
    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
        #自己的token
        token="hfli" #这里改写你在微信公众平台里输入的token
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法        
        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr

    def POST(self):        
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        fromUser=xml.find("FromUserName").text
        toUser=xml.find("ToUserName").text
        msgType=xml.find("MsgType").text
	if msgType=='event':
	    event = xml.find("Event").text
	    if event == 'subscribe':
		return response_text_msg(fromUser,toUser,HELP_INFO)
        content=xml.find("Content").text#获得用户所输入的内容
	if content == u"音乐":
	    title = u"五星红旗迎风飘扬"
	    description= u"五星红旗迎风飘扬，胜利歌声多么嘹亮。。。"
	    url = "http://attachment2.tgbusdata.cn/3/091112/462823.mp3"
	    hqurl = "http://attachment2.tgbusdata.cn/3/091112/462823.mp3"
	    return response_music_msg(fromUser,toUser,title,description,url,hqurl)
        music_url = "http://box.zhangmen.baidu.com/x?op=12&count=1&title=%s$$"%(urllib2.quote(content.encode("utf-8")))
#        music_url = "http://box.zhangmen.baidu.com/x?op=12&count=1&title=%E5%A4%A7%E7%BA%A6%E5%9C%A8%E5%86%AC%E5%AD%A3$$"
        try:
          baidu_data = urllib2.urlopen(music_url).read()
        except:
          return response_text_msg(fromUser,toUser,u"服务器异常")
        url = re.findall('<url>.*?</url>',baidu_data)
        if url == []:
            return response_text_msg(fromUser,toUser,u"没有该歌曲")
        url1 = re.findall('<encode>.*?CDATA\[(.*?)\]].*?</encode>',url[0])
        url1 = url1[0][:url1[0].rindex('/')+1]
        url2 = re.findall('<decode>.*?CDATA\[(.*?)\]].*?</decode>',url[0])
        if url2[0].find('&') != -1:
            url2 = url2[0][:url2[0].rindex('&')]
        else:
            url2 = url2[0][:]
        url1 += url2
        desc = u"来自百度音乐"
        return response_music_msg(fromUser,toUser,content,desc,url1,url1)

