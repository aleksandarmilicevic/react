import copy

_m2_empty = {
    "record": {},
    "machine": {},
    "event": {}
}

_m2 = copy.deepcopy(_m2_empty)

def _records():  return _m2["record"]
def _machines(): return _m2["machine"]
def _events():   return _m2["event"]

def all(kind):  return _m2[kind].values()
def records():  return _records().values()
def machines(): return _machines().values()
def events():   return _events().values()

def find(kind, id): 
    return _m2[kind][id]

def record(id):   return _records()[id]
def machine(id):  return _machines()[id]
def event(id):    return _events()[id]

def _add_to(kind, robj): 
    _m2[kind][robj.id()] = robj

def add_record(robj):   _add_to(_records(), robj)
def add_machine(robj):  _add_to(_machines(), robj)
def add_event(robj):    _add_to(_events(), robj)

def reset():
    global _m2
    _m2 = copy.deepcopy(_m2_empty)
