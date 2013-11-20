
from struct import Struct

class StructBase(Struct):
    def unpacking(self, bytes, offset):
        return self.unpack_from(bytes, offset), offset + self.size

class StructBaseSingle(Struct):
    def unpacking(self, bytes, offset):
        return self.unpack_from(bytes, offset)[0], offset + self.size

STRUCT_BYTE = StructBaseSingle('!B')
STRUCT_SHORT = StructBaseSingle('!H')
STRUCT_INT = StructBaseSingle('!I')

class StructList(object):

    def __init__(self, sub, idx=STRUCT_BYTE):
        self.sub = sub
        self.idx = idx
    
    def pack(self, alist):
        bytes = self.idx.pack(len(alist))
        return bytes + ''.join((self.sub.pack(e) for e in alist))
    
    def unpacking(self, bytes, offset):
        n, offset = self.idx.unpacking(bytes, offset)
        alist = []
        for _ in range(n):
            e, offset = self.sub.unpacking(bytes, offset)
            alist.append(e)
        return alist, offset

class StructTuple(object):

    def __init__(self, sub, size):
        self.sub = sub
        self.size = size
    
    def pack(self, alist):
        if len(alist) != self.size: raise Exception("Wrong size!")
        return ''.join((self.sub.pack(e) for e in alist))
    
    def unpacking(self, bytes, offset):
        alist = []
        for _ in range(self.size):
            e, offset = self.sub.unpacking(bytes, offset)
            alist.append(e)
        return alist, offset
