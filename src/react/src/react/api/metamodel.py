import react
from react import meta
from react import db
from react.api.types import Type

class ReactObjMClass(type):
    def __call__(cls, *args, **kwargs):
        """
        Intercept constructor calls and register created instances with react.db
        """
        obj = super(ReactObjMClass, cls).__call__(*args, **kwargs)
        react.db._add_to(cls.kind(), obj)
        return obj

    # def __new__(meta, name, bases, dct):
    #     return super(ReactObjMClass, meta).__new__(meta, name, bases, dct)
        
    def __init__(cls, name, bases, dct):
        """
        Intercept subclass definitions and register defined subclasses with react.meta
        """
        super(ReactObjMClass, cls).__init__(name, bases, dct)
        if cls.is_record():    meta_obj = RecordMeta(cls)            
        elif cls.is_machine(): meta_obj = MachineMeta(cls)
        elif cls.is_event():   meta_obj = EventMeta(cls)
        else:                  meta_obj = None
        if not meta_obj is None: 
            cls.meta_obj = meta_obj
            react.meta._add_to(cls.kind(), cls.meta_obj)

    def fields(cls, **kwargs):
        flds = [(k, Type.get(v)) for (k, v) in kwargs.iteritems()]
        cls.meta().fields().update(flds)
    

class RecordMeta(object):
    def __init__(self, cls):
        self._cls = cls
        self._fields = dict()

    def name(self):     return self._cls.__name__
    def cls(self):      return self._cls
    def obj_type(self): return self.cls()
    def fields(self):   return self._fields

class MachineMeta(RecordMeta):
    pass

class EventMeta(RecordMeta):
    pass
