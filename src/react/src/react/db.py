import copy

_m2_empty = {
    "record": {},
    "machine": {},
    "event": {}
}

_m2 = copy.deepcopy(_m2_empty)

def _find_in(kind, id): 
    return _m2[kind][id]

def find_record(id):   return _find_in("record", id)
def find_machine(id):  return _find_in("machine", id)
def find_event(id):    return _find_in("event", id)

def _add_to(kind, robj): 
    _m2[kind][robj.id()] = robj

def add_record(robj):   _add_to("record", robj)
def add_machine(robj):  _add_to("machine", robj)
def add_event(robj):    _add_to("event", rmeta)

def reset():
    global _m2
    _m2 = copy.deepcopy(_m2_empty)
