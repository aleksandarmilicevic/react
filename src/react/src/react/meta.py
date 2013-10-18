import copy

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
    return dct[name]

def record(name):   return find("record", name)
def machine(name):  return find("machine", name)
def event(name):    return find("event", name)

def _add_to(kind, rmeta): 
    dct = _get_dct_for(kind)
    dct[rmeta.name()] = rmeta

def add_record(rmeta):   _add_to("record", rmeta)
def add_machine(rmeta):  _add_to("machine", rmeta)
def add_event(rmeta):    _add_to("event", rmeta)

def reset():
    global _m1
    _m1 = copy.deepcopy(_m1_empty)
