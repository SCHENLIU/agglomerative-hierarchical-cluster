#!/bin/env python2.7
#coding:utf-8
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException
import traceback
import json
import math
from datetime import datetime
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

_cur_dir = os.path.dirname(os.path.realpath(__file__))
from rpc.article_thrift_helper import *
sys.path.append(_cur_dir + '/gen-py')
from dssm_service.ttypes import *
from dssm_service import  NLPService
from thrift_base import ThriftClientBase,ThriftNonblockClientBase
import time
import random

class DssmClient(ThriftNonblockClientBase):
    def __init__(self,host='multi-dssm-server.nlp.data.sina.com.cn',port=80,timeout=3000,fixHost=True,log=None):
        self.fixHost = fixHost
        self.host = host
        ThriftNonblockClientBase.__init__(self,self.host,port,NLPService,timeout,log)
    def dssm(self, data,traceID=None):
        try:
            ctx = ArticleThriftHelper.gen_ctx(traceID)
            article =  ArticleThriftHelper.to_article(data)
            req = NLPRequest(doc=article)
            res = self.call_remote(self.client.dssm, ctx, req)
            return res

        except Exception as e:
            traceback.print_exc()
            return None

if __name__=='__main__':
    print '------------initializing thrift client-----------'
    nc = DssmClient(host='multi-dssm-server.nlp.data.sina.com.cn',fixHost=True,timeout=6000,port=80)
    print nc.host
    print '-----------------------------------------'
    try:
        content = ' '

        ti="美联储副主席称资产负债表和额外的前瞻性指引都是备选政策"
        import time
        start_ = time.time()
        loop = 0
        #data = {'title': ti, 'content': content, 'model': 'albert_dssm'}
        data = {'title': ti, 'content': content, 'model': 'news_dssm'}
        while loop < 1:
            loop += 1
            st_ = time.time()
            kws = nc.dssm(data)
            print(kws)
            print("time used:{:.2f}ms".format(1000*(time.time()-st_)))
        end_ = time.time()


        print("model:{}; loop: {}; avg time used:{}ms".format('weibo_dssm', loop, (end_-start_)*1000/loop))
    except KeyboardInterrupt:
        print 'bye!'
    except Exception,e:
        print e
    finally:
        print 'finally'
        nc.close()
