from .metamodel import *

from react import db

class ReactObj(): 
    __metaclass__ = ReactObjMClass

    id_cnt = 0

    def __init__(self, **kwargs):
        ReactObj.id_cnt = ReactObj.id_cnt + 1
        self._id = ReactObj.id_cnt
        self._init_fields()

    @classmethod
    def alias_for(cls, id):
        obj = cls.__new__(cls)
        obj._id = id
        obj._init_fields()
        return obj

    @classmethod
    def is_record(cls):  return False
    
    @classmethod 
    def is_machine(cls): return False
    
    @classmethod 
    def is_event(cls):   return False

    @classmethod
    def kind(cls):
        if cls.is_event():     return "event"
        elif cls.is_machine(): return "machine"
        elif cls.is_record():  return "record"
        else:                  return None

    @classmethod
    def meta(target): 
        if isinstance(target, ReactObj):   return type(target).meta()
        elif issubclass(target, ReactObj): return target.meta_obj
        else: 
            raise RuntimeException("unexpected argument type: %s" % target)

    @classmethod
    def all(cls): return filter(lambda r: isinstance(r, cls), db.all(cls.kind()))
        
    def id(self): return self._id

    def _init_fields(self):
        for fname, ftype in self.meta().fields().iteritems():
            setattr(self, fname, ftype.default_value())


def new_react_cls(__name, __bases, **fields):
    cls = type(__name, __bases, {})
    cls.fields(**fields)
    return cls

class Record(ReactObj):
    @classmethod 
    def is_record(cls): return True

class Machine(ReactObj):
    @classmethod 
    def is_machine(cls): return True

class Event(ReactObj):
    @classmethod 
    def is_event(cls): return True

    def guard(self):   return None
    def handler(self): return None

def record(__name, **fields):  return new_react_cls(__name, (Record,), **fields)
def machine(__name, **fields): return new_react_cls(__name, (Machine,), **fields)
def event(__name, **fields):   return new_react_cls(__name, (Event,), **fields)
    
