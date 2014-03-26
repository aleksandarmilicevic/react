import copy
import thread

from .metamodel import *
from react import db
from react.api.wrappers import *

class ReactObj(object):
    __metaclass__ = ReactObjMClass

    _id_cnt = 0
    _attr_access_listeners = []

    def __init__(self, **kwargs):
        """
        @param **kwargs dict<str, object>; initial field values
        """
        ReactObj._id_cnt = ReactObj._id_cnt + 1
        self._id = ReactObj._id_cnt
        self._init_fields()
        for fname, fvalue in kwargs.iteritems():
            self.set_field(fname, fvalue)

    def __str__(self):
        return "%s(%d)" % (self.meta().name(), self.id())

    def __repr__(self):
        flds = []
        for fld_name, fld_type in self.meta().fields().iteritems():
            val = unwrap(getattr(self, fld_name))
            if fld_type.is_primitive():
                val_str = repr(val)
            else:
                val_str = str(val)
            flds.append("%s: %s" % (fld_name, val_str))
        fields_str = ", ".join(flds)
        return "<%s(%d) { %s }>" % (self.meta().name(), self.id(), fields_str)

    @classmethod
    def find_or_new(cls, id):
        try:
            return react.db.find(cls.kind(), id)
        except Exception, e:
            obj = cls.alias_obj(id)
            react.db.add(cls.kind(), obj)
            return obj

    @classmethod
    def alias_obj(cls, id):
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

    @classmethod
    def where(cls, **kw):
        def matches(robj):
            for fname, fvalue in kw.iteritems():
                if not getattr(robj, fname) == fvalue:
                    return False
            return True
        return filter(matches, cls.all())

    @classmethod
    def find(cls, id): return react.db.find(cls.kind(), id)

    @classmethod
    def attr_access_listeners(cls):          return copy.copy(cls._attr_access_listeners)
    @classmethod
    def add_access_listener(cls, lstner):    cls._attr_access_listeners.append(lstner)
    @classmethod
    def remove_access_listener(cls, lstner): cls._attr_access_listeners.remove(lstner)
    @classmethod
    def notify_listeners(cls, *args):
        for lstner in cls.attr_access_listeners():
            lstner(*args)

    def _field_mutated(self, fname, fvalue):
        ReactObj.notify_listeners("write", self, fname, fvalue)

    def __getattribute__(self, name):
        meta = object.__getattribute__(self, "meta")()
        fld_names = meta.fields().keys()
        value = object.__getattribute__(self, name)
        if name in fld_names:
            ReactObj.notify_listeners("read", self, name)
            value = Wrapper.wrap(value, self, name)
        return value

    def __setattr__(self, name, value):
        fld_names = object.__getattribute__(self, "meta")().fields().keys()
        if name in fld_names:
            value = unwrap(value)
            ReactObj.notify_listeners("write", self, name, value)
        object.__setattr__(self, name, value)

    def id(self): return self._id

    def get_field(self, fname):
        """
        returns the value of field `fname'
        """
        return getattr(self, fname)

    def set_field(self, fname, fvalue):
        """
        sets the value of field `fname' to `fvalue'
        """
        return setattr(self, fname, fvalue)

    def delete(self):
        react.db.delete(self.meta().cls().kind(), self)

    def _init_fields(self):
        """
        initializes all fields from self.meta() with default values
        """
        for fname, ftype in self.meta().fields().iteritems():
            self.set_field(fname, ftype.default_value())

class Record(ReactObj):
    @classmethod
    def is_record(cls): return True

class Machine(ReactObj):
    @classmethod
    def is_machine(cls): return True

    def exit(self):
        thread.interrupt_main()

    def trigger(self, ev):
        ev.set_sender(self)
        if ev.get_receiver() is None:
            ev.set_receiver(react.core.events.find_implicit_receiver(type(ev)))
        return react.core.events.call_event_service(ev)

class Event(ReactObj):
    @classmethod
    def is_event(cls): return True

    @classmethod
    def find_or_new(cls, id):
        return cls()

    def get_sender(self):      return self.get_field("sender")
    def get_receiver(self):    return self.get_field("receiver")
    def set_sender(self, m):   return self.set_field("sender", m)
    def set_receiver(self, m): return self.set_field("receiver", m)

    def guard(self):
        if hasattr(self, "whenever"):
            if self.whenever():
                return None
            else:
                return "whenever condition not met"
        else:
            return None
    def handler(self):      return None

    def get_field(self, fname):
        call_super = lambda n: super(Event, self).get_field(n)
        if fname == "sender":     return call_super(self.meta().sender_fld_name())
        elif fname == "receiver": return call_super(self.meta().receiver_fld_name())
        else:                     return call_super(fname)

    def set_field(self, fname, fvalue):
        call_super = lambda n, v: super(Event, self).set_field(n, v)
        if fname == "sender":     call_super(self.meta().sender_fld_name(), fvalue)
        elif fname == "receiver": call_super(self.meta().receiver_fld_name(), fvalue)
        else:                     call_super(fname, fvalue)

class WheneverEvent(Event):
    @classmethod
    def instantiate(cls, receiver):
        return [cls(receiver=receiver)]
