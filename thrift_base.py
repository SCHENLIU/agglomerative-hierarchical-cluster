#!/bin/env python2.7
#coding:utf-8
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol,TCompactProtocol
from thrift.server import TServer
from thrift.server import TNonblockingServer
from datetime import datetime
import traceback
import socket
import signal
import sys
import logging 

def signal_handler(signum, frame):
    print 'accept signal %d at %s, now exiting' %(signum,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    exit(0)

class ThriftServerBase:
    def __init__(self,port,handler,service,threads_num=12):
        self.port = port
        self.handler = handler
        self.service = service
        self.threads_num = threads_num
        #logging.basicConfig(level=logging.INFO,filename='./%s.log'%self.__class__.__name__)
        self.log = logging.getLogger("ThriftServerBase")
    def serve(self):
        signal.signal(signal.SIGTERM,signal_handler)
        signal.signal(signal.SIGUSR1,signal_handler)
        #handler = NLPServiceHandler()
        processor = self.service.Processor(self.handler)
        tsocket = TSocket.TServerSocket(port=self.port)
        ttransport = TTransport.TBufferedTransportFactory()
        #tprotocol = TBinaryProtocol.TBinaryProtocolFactory()
        pfactory = TCompactProtocol.TCompactProtocolFactory()

        #server = TServer.TSimpleServer(processor, tsocket, ttransport, tprotocol)
        # You could do one of these for a multithreaded server
        #server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
        server = TServer.TThreadPoolServer(processor, tsocket, ttransport, pfactory)
        server.setNumThreads(self.threads_num)

        print datetime.now(),' Starting thrift server on port %d...'%self.port
        server.serve()
        print datetime.now(),' thrift server quit.'
            

class ThriftClientBase:
    def __init__(self,host,port,service,timeout=2000,log=None):
        self.host = host
        self.port = port
        self.service = service
        self.transport = None
        self.timeout = timeout
        self.connect()
        if not log:
            #logging.basicConfig(level=logging.INFO,filename='./%s.log'%self.__class__.__name__)
            #logging.basicConfig(level=logging.WARNING)
            self.log = logging.getLogger("ThriftClientBase")
        else:
            self.log = log
    def _before_reconnect(self):
        pass
    def connect(self):
        if self.transport:
            self.close()
            self._before_reconnect()

        self.transport = TSocket.TSocket(self.host,self.port)
        # Buffering is critical. Raw sockets are very slow
        if self.timeout > 0:
            self.transport.setTimeout(self.timeout)
        self.transport = TTransport.TBufferedTransport(self.transport)
        # Wrap in a protocol
        #protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        protocol = TCompactProtocol.TCompactProtocol(self.transport)
        # Create a client to use the protocol encoder
        self.client = self.service.Client(protocol)
        # Connect!
        self.transport.open()

    def __del__(self):
        if self.transport:
            self.transport.close()

    def close(self):
        self.transport.close()
        self.transport = None
    def call_remote(self,fnc,*args):
        '''远程调用的包装方法，用于统一处理调用失败时重新连接服务器
       比如，在客户端要调用服务端的方法foo(arg1,arg2,arg3),需要在客户端
       做如下定义：
       def foo(self,arg1,arg2,arg3):
            #对参数做一些操作,然后调用call_wrapper
            return self.call_remote(self.client.foo,arg1,arg2,arg3)
                
        '''

        retries = 3
        while retries:
            try:
                return fnc(*args)
            except (socket.timeout,socket.error) as e:
                #traceback.print_exc()
#                self.log.error(e)
                #self.log.error(traceback.format_exc())
                self.connect()
                #return None
            except Thrift.TException as tx:
                #traceback.print_exc()
                #self.log.error(traceback.format_exc())
                self.connect()
                return None
            retries -= 1
        return None

class ThriftNonblockServerBase(object):
    def __init__(self,port,handler,service,threads_num=12):
        self.port = port
        self.handler = handler
        self.service = service
        self.threads_num = threads_num
        #logging.basicConfig(level=logging.DEBUG)
        #logging.basicConfig(level=logging.DEBUG,filename='./%s.log'%self.__class__.__name__)
        self.log = logging.getLogger("ThriftServerBase")

    def serve(self):
        signal.signal(signal.SIGTERM,signal_handler)
        signal.signal(signal.SIGUSR1,signal_handler)
        processor = self.service.Processor(self.handler)
        tsocket = TSocket.TServerSocket(port=self.port)

        ttransport = TCompactProtocol.TCompactProtocolFactory()
        pfactory = TCompactProtocol.TCompactProtocolFactory()

        server = TNonblockingServer.TNonblockingServer(processor, tsocket, ttransport, pfactory)
        server.setNumThreads(self.threads_num)

        print datetime.now(),' Starting thrift server on port %d...'%self.port
        server.serve()
        print datetime.now(),' thrift server quit.'
            

class ThriftNonblockClientBase(object):
    def __init__(self,host,port,service,timeout=2000,log=None):
        self.host = host
        self.port = port
        self.service = service
        self.transport = None
        self.timeout = timeout
        self.connect()
        if not log:
            #logging.basicConfig(level=logging.INFO,filename='./%s.log'%self.__class__.__name__)
            self.log = logging.getLogger("ThriftClientBase")
        else: self.log = log
    def _before_reconnect(self):
        pass
    def connect(self):
        if self.transport:
            self.close()
            self._before_reconnect()

        self.transport = TSocket.TSocket(self.host,self.port)
        # Buffering is critical. Raw sockets are very slow
        if self.timeout > 0:
            self.transport.setTimeout(self.timeout)
        self.transport = TTransport.TFramedTransport(self.transport)
        # Wrap in a protocol
        protocol = TCompactProtocol.TCompactProtocol(self.transport)
        # Create a client to use the protocol encoder
        self.client = self.service.Client(protocol)
        # Connect!
        self.transport.open()

    def __del__(self):
        if self.transport:
            self.transport.close()

    def close(self):
        self.transport.close()
        self.transport = None
    def call_remote(self,fnc,*args):
        '''远程调用的包装方法，用于统一处理调用失败时重新连接服务器
       比如，在客户端要调用服务端的方法foo(arg1,arg2,arg3),需要在客户端
       做如下定义：
       def foo(self,arg1,arg2,arg3):
            #对参数做一些操作,然后调用call_wrapper
            return self.call_remote(self.client.foo,arg1,arg2,arg3)
                
        '''

        retries = 3
        while retries:
            try:
                return fnc(*args)
            except (socket.timeout,socket.error) as e:
                #self.log.error(traceback.format_exc())
                self.connect()
                #return None
            except Thrift.TException, tx:
                #self.log.error(traceback.format_exc())
                self.connect()
                return None
            except:# TTransportException:
                #print traceback.format_exc()
                #self.log.error(traceback.format_exc())
                self.connect()
                return None
            retries -= 1
        return None

if __name__=='__main__':
    from util.local_setting import *
    sys.path.append(WORKSPACE+'rpc/gen-py')
    from nlp.ttypes import *
    from nlp import  NLPService
    from rpc.nlp_thrift_server import NLPServiceHandler
    if sys.argv[1] == 'server':
        print '-------demo for derive class from ThriftServerBase-----'
        ThriftServerBase(30001,NLPServiceHandler(),NLPService).serve()
    else:
        print '-------demo for derive class from ThriftClientBase-----'
        print ' a client implement nlpclient '
        print '--'*10
        import json
        class NlpClient(ThriftClientBase):
            def __init__(self,host=NLP_COMMON_HOST,port=30001):
                ThriftClientBase.__init__(self,host, port,NLPService)
            def split(self,request, encoding='unicode'):
                def do_split(obj,requst,encoding):
                    data = obj.client.split(request)
                    res =  json.loads(data)
                    if encoding == 'utf-8':
                        for word in res:
                            word['word'] = word['word'].encode('utf-8')
                            for i in range(0,len(word.get('small_words',[]))):
                                word['small_words'][i] = word['small_words'][i].encode('utf-8')
                    return res 
                return self.call_remote(do_split,self,request,encoding)

        clt = NlpClient()
        obj = clt.split('打个大西瓜')
        print json.dumps(obj,ensure_ascii=False)

