import copy
import react
from react.api import types

_m1_empty = {
    "record": {},
    "machine": {},
    "event": {}
}

_m1 = copy.deepcopy(_m1_empty)

def _get_dct_for(kind):
    return _m1[kind]

def find(kind, name):
    dct = _get_dct_for(kind)
    return dct.get(name)

def record(name):   return find("record", name)
def machine(name):  return find("machine", name)
def event(name):    return find("event", name)

def add(kind, rmeta):
    dct = _get_dct_for(kind)
    dct[rmeta.name()] = rmeta

def add_record(rmeta):  add("record", rmeta)
def add_machine(rmeta): add("machine", rmeta)
def add_event(rmeta):   add("event", rmeta)

def find_whenever_events(receiver_machine_cls):
    def whenever_filter_func(ev_meta):
        return types.issubtype(ev_meta.receiver(), receiver_machine_cls) and hasattr(ev_meta.cls(), "whenever")

    return filter(whenever_filter_func, _get_dct_for("event").values())

def reset():
    global _m1
    _m1 = copy.deepcopy(_m1_empty)
