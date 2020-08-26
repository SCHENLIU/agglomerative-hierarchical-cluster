import json
import os
import sys

_cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_cur_dir + '/gen-py')

import article_thrift
import article_thrift.ttypes

from article_thrift.ttypes import *

from util.utils import socket_get_host_ip
import time

_ip = socket_get_host_ip()

_article_keys = set()
for t in ArticleThrift.thrift_spec[1:]:
    _article_keys.add(t[2])


class ArticleThriftHelper:
    @staticmethod
    def to_dict(article):
        data = {}
        for k,v in vars(article).iteritems():
            if v != None: data[k] = v
        if "json_str" in data: 
            extra = json.loads(data.pop('json_str'))
            data.update(extra)

        return data

    @staticmethod
    def to_article(data):
        doc = ArticleThrift()
        extra = {}
        for k,v in data.iteritems():
            if k in _article_keys:
                if isinstance(v,unicode): v = v.encode('utf8')
                if k == 'ztlevel' and  not ( -2147483648 < v < 2147483648): v = 0
                setattr(doc,k,v)
            else:
                extra[k] = v
        if extra: doc.json_str = json.dumps(extra,ensure_ascii=False).encode('utf8')
        return doc
    @staticmethod
    def gen_ctx(traceID = None):
        if not traceID: traceID = "%s:%.6f" % (_ip, time.time())
        ctx = RpcContext(traceID)
        return ctx
        

