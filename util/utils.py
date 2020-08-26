#!/bin/env python2.7
#coding:utf-8

import uuid
import json
import traceback
import os
from datetime import date,datetime
import time
import urllib2
import urllib
from collections import namedtuple
import re
import random
import stat
import socket
import tarfile


#operator type for interface call worker
interface_call_operators = ['resize_image','crop_image','gen_commentid','gen_newsid_weibourl','gen_zt_level','gen_edit_level']
INTERFACE_CALL_TYPE = namedtuple('Enum', ' '.join(interface_call_operators).upper())(*interface_call_operators)

def get_uuid(url):
    '''
    url should be encoded in utf-8
    '''
    if isinstance(url,unicode):
        url = url.encode('utf-8')
    return str(uuid.uuid3(uuid.NAMESPACE_URL,url)).replace('-','')

def my_sleep(sec):
    try:
        time.sleep(sec)
    except KeyboardInterrupt:
        print 'bye!'
        exit(0)


def send_simple_mail(subject,content,cc='',to='',mtype='txt'):
    params = {'from':'simba','title':subject,'content':content,'cc':cc,'mtype':mtype}
    if to:
        params['to'] = to
    urllib2.urlopen("http://10.13.3.36:8899/p/sendmail",urllib.urlencode(params),timeout=5).read()

class MyException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def full2half(s):
    n = []
    if not isinstance(s,unicode): s = s.decode('utf-8','ignore')
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        num = unichr(num)
        n.append(num)
    return ''.join(n)

def ascii_word_count(s):
    if not isinstance(s,unicode): s = s.decode('utf-8')
    cnt = 0
    for i in s:
        if ord(i) < 128 : cnt += 0.5
        else: cnt += 1
    return cnt

def get_img_path(img_url):
    '''get image path'''
    ''' hash the last two uuid number to generate 256 folders'''
    save_path ='/data0/nfs_data/image/' 
    uuid = get_uuid(img_url)
    num1 = uuid[-2:]
    num1 = int('0x'+num1,16)
    num2 = uuid[-4:-2]
    num2 = int('0x'+num2,16)
    save_path += str(num1)+'/'+str(num2)
    if not os.path.exists(save_path):
        try:
            os.makedirs(save_path)
        except OSError as e:
            pass
    itype = img_url.split('.')[-1]
    if itype == 'png':
        save_path += '/'+uuid+'.png'
    else:
        save_path += '/'+uuid+'.jpg'
    return save_path

def get_video_path(uuid,save_path='/sinarecmd/video/'):
    ''' get video path'''
    ''' hash the last two uuid number to generate 256 folders'''
    num = uuid[-2:]
    num = int('0x'+num,16)
    save_path += '/'+str(num)
    if not os.path.exists(save_path):
        try:
            os.mkdir(save_path)
        except OSError as e:
            pass
        os.chmod(save_path,stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
    save_path += '/'+uuid
    return save_path


'''
错误提示列表：
-1:没有从mongoDB取到数据
-2:获取视频来源失败
-3:获取视频播放地址失败
-4:微博token过期
-5:获取下载地址时没有找到对应视频类型
-6:未知视频后缀类型
-7:视频下载超时
0,1:视频已下载
'''

def filter_emoji(desstr,restr=''):
    '''
    filter emoji
    '''
    try:
        if not isinstance(desstr,unicode):
            desstr = desstr.decode('utf-8')
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error: 
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')  
        return co.sub(restr, desstr)
    except:
        pass
    return desstr
word_valid_pos = {
     100: 80, #名词
     103: 50, #动词
     104: 30, #简称略语
     107: 10, #区别词
     108: 100, #人名
     109: 250, #其他专名
     110: 100, #人名
     #111:100, #名语素
     112: 50, #非汉字 
     113: 100, #地名
     118: 100, #
     120: 50, #动词功能成语
     121: 50, #名词功能成语
     123: 200, #名词功能简称
     127: 50, #名动词
     128: 50, #名
     131: 100, #不及物动词
     133: 100, #名词功能习用语
     140: 100, #机构团体
     141: 100, #区别功能词
     142: 100, #专名时间词
     150: 50, #动语素
     154: 50, #形式动词
     163: 100, #名形词
}


def filtered_word(w):
    if not w: return True
    w = full2half(w)
    if len(w) > 8 or len(w) < 2: return True
    if re.search(u'[0-9\./一二三四五六七八九十%:：_\-]{1,}[a-zA-Z年月日时分秒千百万亿]{0,}',w): return True
    for f in [ u'http',u'com',u'www',u'org',u'net',u'ftp',u'cn']:
        if f in w: return True
    return False

__fg_dict={
        'black':30,#（黑色）
        'b':30,#（黑色）
        'red':31,#（红色）
        'r':31,#（红色）
        'green':32,#（绿色）
        'g':32,#（绿色）
        'yellow':33,#（黄色）
        'y':33,#（黄色）
        'blue':34,#（蓝色）
        'bl':34,#（蓝色）
        'magenta':35,#（洋 红）
        'm':35,#（洋 红）
        'cyan':36,#（青色）
        'c':36,#（青色）
        'white':37,#（白色）
        'w':37,#（白色）
        }
__bg_dict={
        'black':40,#（黑色）
        'b':40,#（黑色）
        'red':41,#（红色）
        'r':41,#（红色）
        'green':42,#（绿色）
        'g':42,#（绿色）
        'yellow':43,#（黄色）
        'y':43,#（黄色）
        'blue':44,#（蓝色）
        'bl':44,#（蓝色）
        'magenta':45,#（洋 红）
        'm':45,#（洋 红）
        'cyan':46,#（青色）
        'c':46,#（青色）
        'white':47,#（白色）
        'w':47,#（白色）
        }
__tp_dict={'normal':0,    #（默认值）
        'hl':1, #（高亮） highlight
        'highlight':1, #（高亮） highlight
        'b':2,   #（粗体） bolder
        'bolder':2,   #（粗体） bolder
        'nob':22,   #（非粗体） unbolder
        'nobolder':22,   #（非粗体） unbolder
        'underline':4, #（下划线） underline
        'ul':4, #（下划线） underline
        'noul':24,#（非下划线） 
        'nounderline':24,#（非下划线） 
        'bl':5,#（闪烁）
        'bling':5,#（闪烁）
        'nobl':25,#（非闪烁）
        'nobling':25,#（非闪烁）
        'r':7,#（反显） reverse
        'reverse':7,#（反显） reverse
        'nor':27,#（非反显）
        'noreverse':27,#（非反显）
        }
def color_text(text,fg='red',bg='',tp=''):
    style = [] 
    if tp: style.append(__tp_dict[tp])
    if fg: style.append(__fg_dict[fg])
    if bg: style.append(__bg_dict[bg])
    style = [str(i) for i in style]
    if not style: style = '0'
    else: style = ';'.join(style)


    return '\033[%sm%s\033[0m'%(style,text)
class RandomHost:
    def __init__(self,hosts):
        self._hosts = hosts
        random.seed(int(time.time()))
    def next(self):
        host = self._hosts[random.randint(0,len(self._hosts) - 1)]
        return host

 
def socket_get_host_ip():
    ip = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close() 
    return ip

class IpHashedHost:
    def __init__(self,hosts):
        self._hosts = hosts
        random.seed(int(time.time()))
        self.last_index = random.randint(0,len(self._hosts) - 1)

        try:
            ip = socket_get_host_ip()
            iplast = int ( ip.split('.')[-1] )
            self.last_index = iplast % len(self._hosts)
        except:
            pass
    def next(self):
        host = self._hosts[self.last_index]
        self.last_index = (self.last_index + 1) % len(self._hosts)
        return host
WEIBO_PATTERN= u'\.\.\.|\[(ali亲一个|ali僵尸跳|ali哇|ali得瑟|ali狂笑|ali甩手|ali羞|ali转|ali飘过|bed啦啦啦|bh彪悍|bm亲吻|bm可爱|bm喜悦|bm生气|bm血泪|bm讨论|bm震惊|BOBO哈哈|bofu啃西瓜|cai庆祝|cai脱光|c囧|c得意笑|c摇头萌|c正经|c羞涩|c脸红|c迷糊|dino高兴|din抓狂|din推撞|din脸红|dx洗澡|good|gst呀咩爹|gst耐你|g咀嚼|g喝茶|kiss|km呜血泪|km闪|K兵加油|lm花痴|lt切克闹|lt拍桌大笑|lt摇摆|lt江南style|lxhx咻|lxhx奔跑|moc转发|nono星星眼|ok|ppb叮叮当|ppb狂吃|ppb鼓掌|toto我最摇滚|xkl喜|xkl期待|xkl石化|yz招财猫|下雨|不要|乐乐|互相膜拜|互粉|亲亲|伤心|做鬼脸|偷乐|偷笑|兔子|加油|加油啊|印迹|可怜|可爱|右哼哼|吃惊|吐|听音乐|呵呵|咆哮|咖啡|哈哈|哭|哼|啦啦|嘘|嘻嘻|囧|困|围观|圣诞树|太开心|太阳|失望|奋斗|奥特曼|奥运金牌|好可怜|好喜欢|好激动|委屈|威武|害羞|崩溃|左哼哼|干杯|庆祝|弱|得瑟|微博蛋糕|微风|心|怒|怒骂|思考|悲伤|惊恐|懒得理你|手机|打哈欠|抓狂|抱抱|拜拜|挖鼻屎|挤眼|摊手|晕|月亮|来|汗|江南style|泪|泪流满面|浮云|熊猫|爱|爱你|爱心传递|牛|狗|猪头|生病|疑问|痞痞兔囧|睡觉|礼物|神马|笑哈哈|给力|绿丝带|耶|脸红自爆|膜拜了|色|色眯眯|花心|草泥马|萌|落叶|蛋糕|蜡烛|衰|讥笑|许愿|话筒|调戏|赞|路过这儿|跳舞花|转发|鄙视|酒壶|酷|酷库熊微笑|酷库熊怒|金元宝|钟|钱|闭嘴|阳光|阴天|阴险|雨伞|风扇|飞机|馋嘴|鲜花|鼓掌)\]'
def filter_weibo_emoji(text):
    if not isinstance(text,unicode): text = text.decode('utf-8','ignore')
    text = re.sub(WEIBO_PATTERN,'',text)
    return text
        

if __name__=='__main__':
#    import sys
    print color_text('hello word','red')
    print get_img_path('http://n.sinaimg.cn/sinacn/20170921/7945-fymfcih1694609.jpg')
    print get_uuid('http://finance.sina.com.cn/zt_d/cdwjc')
#    send_multimedia_mail('test','test')
#    send_simple_mail('测试','测试')
    x = '测试一下全半角。转换１２３４５89。ＡＢＣＤＥＦx'
    print ascii_word_count(x)
#    y = full2half(x)
#    print x,type(x),y, type(y)
    x = '不转不是中国人1234xyZ'
    print ascii_word_count(x)
    s = '电视剧都编不出！已婚少妇脚踩三条船 还如此荒唐'
    print ascii_word_count(s)
    s = 'NBA五大双子星组合 乔皮组合难以称雄 OK组合登顶'
    print ascii_word_count(s)
    s = '美国前财政部长怼盖茨 称对机器人征税是“深刻误导”'
    print ascii_word_count(s)
    #downloader test
    #print dr.download_video('1e5938b358bd32e7b72a23068f8251b2','./downloadvideo')
