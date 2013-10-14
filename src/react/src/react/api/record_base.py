from react.utils import *

class RecordBase(object):
    __metaclass__ = RecordMeta

    def __init__(self, **kwargs):
        pass

    @classmethod
    def meta(target): 
        if isinstance(target, RecordBase):
            return type(target).meta()
        elif issubclass(target, RecordBase):
            return target.__metaclass__
        else: print("wtf")
