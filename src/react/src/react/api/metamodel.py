import react

class ReactObjMClass(type):
    def __call__(cls, *args, **kwargs):
        if cls in [react.api.model.Record, react.api.model.Machine, react.api.model.Event]:
            base_cls = ReactObjMClass.__new__(ReactObjMClass, "_B_", (cls,), {})
            base_cls.fields(**kwargs)
            return base_cls
        else:
            return super(ReactObjMClass, cls).__call__(*args, **kwargs)

    def __new__(meta, name, bases, dct):
        return super(ReactObjMClass, meta).__new__(meta, name, bases, dct)
        
    def __init__(cls, name, bases, dct):
        super(ReactObjMClass, cls).__init__(name, bases, dct)
        if   cls.is_record():  cls.meta_obj = RecordMeta(cls)
        elif cls.is_machine(): cls.meta_obj = MachineMeta(cls)
        elif cls.is_event():   cls.meta_obj = EventMeta(cls)

    def fields(cls, **kwargs):
        cls.meta().fields().update(kwargs)
    

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
