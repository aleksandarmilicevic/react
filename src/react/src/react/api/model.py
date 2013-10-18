from .metamodel import *

from react import db

class ReactObj(): 
    __metaclass__ = ReactObjMClass

    id_cnt = 0

    def __init__(self, **kwargs):
        """
        @param **kwargs dict<str, object>; initial field values
        """
        ReactObj.id_cnt = ReactObj.id_cnt + 1
        self._id = ReactObj.id_cnt
        self._init_fields()
        for fname, fvalue in kwargs.iteritems():
            self.set_field(fname, fvalue)

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

    def get_field(self, fname):
        """
        returns the value of field `fname'
        """
        getattr(self, fname)

    def set_field(self, fname, fvalue):  
        """
        sets the value of field `fname' to `fvalue'
        """
        setattr(self, fname, fvalue)

    def _init_fields(self):
        """
        initializes all fields from self.meta() with default values
        """
        for fname, ftype in self.meta().fields().iteritems():
            self.set_field(fname, ftype.default_value()) 


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

    def sender(self):   return self.get_field("sender")
    def receiver(self): return self.get_field("receiver")
    def guard(self):    return None
    def handler(self):  return None

    def get_field(self, fname):
        call_super = lambda n: super(Event, self).get_field(n)
        if fname == "sender":     call_super(self.meta().sender_fld_name())
        elif fname == "receiver": call_super(self.meta().receiver_fld_name())
        call_super(fname)

    def set_field(self, fname, fvalue):
        call_super = lambda n, v: super(Event, self).set_field(n, v)
        if fname == "sender":     call_super(self.meta().sender_fld_name(), fvalue)
        elif fname == "receiver": call_super(self.meta().receiver_fld_name(), fvalue)
        call_super(fname, fvalue)

def record(__name, **fields):  return new_react_cls(__name, (Record,), **fields)
def machine(__name, **fields): return new_react_cls(__name, (Machine,), **fields)
def event(__name, **fields):   return new_react_cls(__name, (Event,), **fields)
    
