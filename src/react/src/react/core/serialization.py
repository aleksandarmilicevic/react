import react
from react.api import model
from react import db
from react import msg
from react import meta

def serialize_objref(robj):
    if isinstance(robj, react.api.model.ReactObj):
        return react.msg.ObjRefMsg(kind      = robj.meta().cls().kind(),
                                   cls_name  = robj.meta().name(),
                                   obj_id    = robj.id(),
                                   value     = "")
    else:
        return react.msg.ObjRefMsg(kind      = "primitive",
                                   cls_name  = type(robj).__name__,
                                   obj_id    = -1,
                                   value     = robj.__str__())

def serialize_objval(robj):
    objref = serialize_objref(robj)
    fld_names = robj.meta().fields().keys()
    fld_vals = map(lambda fname: serialize_objref(getattr(robj, fname)), fld_names)
    return react.msg.ObjValMsg(ref = objref,
                               field_names = fld_names,
                               field_values = fld_vals)

def deserialize_objref(objref_msg):
    if objref_msg.kind == "primitive":
        if objref_msg.cls_name == "NoneType":
            return None
        else:
            cls = __builtins__[objref_msg.cls_name]
            return cls(objref_msg.value)
    else:
        cls_meta = meta.find(objref_msg.kind, objref_msg.cls_name)
        return cls_meta.cls().find_or_new(objref_msg.obj_id)

def deserialize_existing(objref_msg):
    return db.try_find(objref_msg.kind, objref_msg.obj_id)

def deserialize_objval(objval_msg):
    robj = deserialize_objref(objval_msg.ref)
    num_flds = len(objval_msg.field_names)
    for idx in range(num_flds):
        fname = objval_msg.field_names[idx]
        fvalue_ref = objval_msg.field_values[idx]
        setattr(robj, fname, deserialize_objref(fvalue_ref))
    return robj
