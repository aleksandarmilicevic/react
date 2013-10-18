import react
from react import meta
from react import db
from react.api.types import Type

def is_func_type(x):
    tname = type(x).__name__ 
    return tname == "function" or tname == "classmethod" or tname == "staticmethod"

class ReactObjMClass(type):
    def __call__(cls, *args, **kwargs):
        """
        Intercept constructor calls and register created instances with react.db
        """
        obj = super(ReactObjMClass, cls).__call__(*args, **kwargs)
        react.db.add(cls.kind(), obj)
        return obj

    # def __new__(meta, name, bases, dct):
    #     return super(ReactObjMClass, meta).__new__(meta, name, bases, dct)
        
    def __init__(cls, name, bases, dct):
        """
        Intercept class definitions and register defined classes with react.meta
        """
        super(ReactObjMClass, cls).__init__(name, bases, dct)

        # create meta
        if cls.is_record():    meta_obj = RecordMeta(cls, dct)
        elif cls.is_machine(): meta_obj = MachineMeta(cls, dct)
        elif cls.is_event():   meta_obj = EventMeta(cls, dct)
        else:                  meta_obj = None

        if meta_obj is None: return

        # assign meta
        cls.meta_obj = meta_obj

        # register with m1
        react.meta.add(cls.kind(), cls.meta_obj)

    def fields(cls, **kwargs):
        flds = [(k, Type.get(v)) for (k, v) in kwargs.iteritems()]
        cls.meta().fields().update(flds)
    

class RecordMeta(object):
    """
    @attr _cls: type;                        corresponding ReactObj type (class)
    @attr _fields: dict<str, react.api.Type> dict of fields
    """
    def __init__(self, cls, dct):
        self._cls = cls
        self._fields = dict()

        # set fields from dct
        self._iter_dct(dct, self._add_field)

    def name(self):     return self._cls.__name__
    def cls(self):      return self._cls
    def obj_type(self): return self.cls()
    def fields(self):   return self._fields

    def _iter_dct(self, dct, func):
        # import pdb; pdb.set_trace()
        for fname, ftype in dct.iteritems():
            if (not fname.startswith("__")) and (not is_func_type(ftype)):
                func(fname, ftype)

    def _add_field(self, fname, ftype):
        self._fields[fname] = Type.get(ftype)

class MachineMeta(RecordMeta):
    pass

class EventMeta(RecordMeta):
    """
    @attr _sender_fld_name:   str; name of the field pointing to the sender machine
    @attr _receiver_fld_name: str; name of the field pointing to the receiver machine
    """
    def __init__(self, *args, **kwargs):
        self._sender_fld_name = None
        self._receiver_fld_name = None
        super(EventMeta, self).__init__(*args, **kwargs)

    def sender_fld_name(self):   return self._sender_fld_name
    def receiver_fld_name(self): return self._receiver_fld_name

    def _add_field(self, fname, ftype):
        if fname == "sender" or fname == "receiver" or fname == "params":
            self._ctx = fname
            self._iter_dct(ftype, self._add_field_ctx)
        else:
            self._ctx = "params"
            self._add_field_ctx(fname, ftype)

    def _add_field_ctx(self, fname, ftype):
        if self._ctx == "sender":     self._sender_fld_name = fname
        elif self._ctx == "receiver": self._receiver_fld_name = fname
        super(EventMeta, self)._add_field(fname, ftype)

        
