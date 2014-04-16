import pickle
import react
from react import conf
from react import db
from react import msg
from react import meta
from react.api.wrappers import unwrap

def to_refx(obj_ref):
    return react.msg.ObjRefMsgX(kind     = obj_ref.kind,
                                cls_name = obj_ref.cls_name,
                                obj_id   = obj_ref.obj_id,
                                value    = obj_ref.value)

def from_refx(obj_refx):
    return react.msg.ObjRefMsg(kind     = obj_refx.kind,
                               cls_name = obj_refx.cls_name,
                               obj_id   = obj_refx.obj_id,
                               value    = obj_refx.value,
                               elems    = [])


def serialize_objref(robj):
    if isinstance(robj, react.api.model.ReactObj):
        return react.msg.ObjRefMsg(kind      = robj.meta().cls().kind(),
                                   cls_name  = robj.meta().name(),
                                   obj_id    = robj.id(),
                                   value     = "",
                                   elems     = [])
    elif isinstance(robj, list):
        return react.msg.ObjRefMsg(kind      = "list",
                                   cls_name  = "list",
                                   obj_id    = "-1",
                                   value     = "",
                                   elems     = map(lambda o: to_refx(serialize_objref(o)), robj))
    else:
        return react.msg.ObjRefMsg(kind      = "primitive",
                                   cls_name  = type(robj).__name__,
                                   obj_id    = "-1",
                                   value     = str(robj),
                                   elems     = [])

def serialize_objval(robj):
    objref = serialize_objref(robj)
    pser = None
    if not (objref.kind == "primitive" or objref.kind == "list"):
        pser = pickle.dumps(robj);
    fld_names = robj.meta().fields().keys()
    fld_vals = map(lambda fname: serialize_objref(unwrap(getattr(robj, fname))), fld_names)
    return react.msg.ObjValMsg(ref = objref,
                               pickle_str = pser,
                               field_names = fld_names,
                               field_values = fld_vals)

def deserialize_objref(objref_msg):
    if objref_msg.kind == "primitive":
        if objref_msg.cls_name == "NoneType":
            return None
        else:
            cls = __builtins__[objref_msg.cls_name]
            return cls(objref_msg.value)
    elif objref_msg.kind == "list":
        return map(lambda m: deserialize_objref(from_refx(m)), objref_msg.elems)
    else:
        cls_meta = meta.find(objref_msg.kind, objref_msg.cls_name)
        ret = cls_meta.cls().find_or_new(objref_msg.obj_id)
        return ret

def deserialize_existing(objref_msg):
    return db.try_find(objref_msg.kind, objref_msg.obj_id)

def deserialize_objval(objval_msg):
    pstr = objval_msg.pickle_str
    if pstr is not None and len(pstr) > 0:
        robj = pickle.loads(objval_msg.pickle_str)
        robj = react.api.model.ReactObj.translate(robj)
    else:
        robj = deserialize_objref(objval_msg.ref)
        num_flds = len(objval_msg.field_names)
        for idx in range(num_flds):
            fname = objval_msg.field_names[idx]
            fvalue_ref = objval_msg.field_values[idx]
            setattr(robj, fname, deserialize_objref(fvalue_ref))
    return robj
