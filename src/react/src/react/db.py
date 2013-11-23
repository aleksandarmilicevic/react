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

def try_find(kind, id):
    return _m2[kind].get(id)

def record(id):   return _records()[id]
def machine(id):  return _machines()[id]
def event(id):    return _events()[id]

def add(kind, robj):
    _m2[kind][robj.id()] = robj

def add_record(robj):   add("record", robj)
def add_machine(robj):  add("machine", robj)
def add_event(robj):    add("event", robj)

def delete(kind, robj):
    _m2[kind].pop(robj.id())

def del_record(robj):   delete("record", robj)
def del_machine(robj):  delete("machine", robj)
def del_event(robj):    delete("event", robj)

def reset():
    global _m2
    _m2 = copy.deepcopy(_m2_empty)
