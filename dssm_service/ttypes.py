#
# Autogenerated by Thrift Compiler (0.9.1)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
import article_thrift.ttypes


from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None



class NLPRequest:
  """
  Attributes:
   - doc
   - classes
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'doc', (article_thrift.ttypes.ArticleThrift, article_thrift.ttypes.ArticleThrift.thrift_spec), None, ), # 1
    (2, TType.MAP, 'classes', (TType.STRING,None,TType.DOUBLE,None), None, ), # 2
  )

  def __init__(self, doc=None, classes=None,):
    self.doc = doc
    self.classes = classes

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRUCT:
          self.doc = article_thrift.ttypes.ArticleThrift()
          self.doc.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.MAP:
          self.classes = {}
          (_ktype1, _vtype2, _size0 ) = iprot.readMapBegin()
          for _i4 in xrange(_size0):
            _key5 = iprot.readString();
            _val6 = iprot.readDouble();
            self.classes[_key5] = _val6
          iprot.readMapEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('NLPRequest')
    if self.doc is not None:
      oprot.writeFieldBegin('doc', TType.STRUCT, 1)
      self.doc.write(oprot)
      oprot.writeFieldEnd()
    if self.classes is not None:
      oprot.writeFieldBegin('classes', TType.MAP, 2)
      oprot.writeMapBegin(TType.STRING, TType.DOUBLE, len(self.classes))
      for kiter7,viter8 in self.classes.items():
        oprot.writeString(kiter7)
        oprot.writeDouble(viter8)
      oprot.writeMapEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.doc is None:
      raise TProtocol.TProtocolException(message='Required field doc is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class NLPResp:
  """
  Attributes:
   - code
   - msg
   - title_dssm_vec
   - content_dssm_vec
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'code', None, None, ), # 1
    (2, TType.STRING, 'msg', None, None, ), # 2
    (3, TType.STRING, 'title_dssm_vec', None, None, ), # 3
    (4, TType.STRING, 'content_dssm_vec', None, None, ), # 4
  )

  def __init__(self, code=None, msg=None, title_dssm_vec=None, content_dssm_vec=None,):
    self.code = code
    self.msg = msg
    self.title_dssm_vec = title_dssm_vec
    self.content_dssm_vec = content_dssm_vec

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.code = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.msg = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.title_dssm_vec = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.content_dssm_vec = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('NLPResp')
    if self.code is not None:
      oprot.writeFieldBegin('code', TType.I32, 1)
      oprot.writeI32(self.code)
      oprot.writeFieldEnd()
    if self.msg is not None:
      oprot.writeFieldBegin('msg', TType.STRING, 2)
      oprot.writeString(self.msg)
      oprot.writeFieldEnd()
    if self.title_dssm_vec is not None:
      oprot.writeFieldBegin('title_dssm_vec', TType.STRING, 3)
      oprot.writeString(self.title_dssm_vec)
      oprot.writeFieldEnd()
    if self.content_dssm_vec is not None:
      oprot.writeFieldBegin('content_dssm_vec', TType.STRING, 4)
      oprot.writeString(self.content_dssm_vec)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.code is None:
      raise TProtocol.TProtocolException(message='Required field code is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)