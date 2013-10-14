from .metamodel import *

class ReactObj(): 
    __metaclass__ = ReactObjMClass

    def __init__(self, **kwargs):
        pass

    @classmethod
    def is_record(cls):  return False
    
    @classmethod 
    def is_machine(cls): return False
    
    @classmethod 
    def is_event(cls):   return False

    @classmethod
    def meta(target): 
        if isinstance(target, ReactObj):   return type(target).meta()
        elif issubclass(target, ReactObj): return target.meta_obj
        else: 
            raise RuntimeException("unexpected argument type: %s" % target)

def new_react_cls(__name, __bases, **fields):
    cls = type(__name, __bases, {})
    cls.fields(**fields)
    return cls

class Record(ReactObj):
    @classmethod 
    def is_record(cls): return True

class Machine(ReactObj):
    def __call__(cls, *args, **kwargs):
        return 3

    @classmethod 
    def is_machine(cls): return True

class Event(ReactObj):
    def __call__(cls, *args, **kwargs):
        return 3

    @classmethod 
    def is_event(cls): return True

def record(__name, **fields):  return new_react_cls(__name, (Record,), **fields)
def machine(__name, **fields): return new_react_cls(__name, (Machine,), **fields)
def event(__name, **fields):   return new_react_cls(__name, (Event,), **fields)
    
