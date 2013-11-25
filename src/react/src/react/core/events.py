import rospy
import react
from react import meta
from react import srv
from react import msg
from react.api.model import *

def node_name(machine):
    return "%s_%s" % (machine.meta().name(), machine.id())

def event_srv_name(machine):
    return "%s_%s" % (react.core.EVENT_SRV_NAME, node_name(machine))

def call_event_service(ev):
    ev_service = rospy.ServiceProxy(event_srv_name(ev.get_receiver()), react.srv.EventSrv)
    # ev_service = rospy.ServiceProxy(react.core.EVENT_SRV_NAME, react.srv.EventSrv)
    ev_msg = react.core.serialization.serialize_objval(ev)
    return ev_service(ev_msg)

def find_implicit_receiver(ev_cls):
    receiver_cls = ev_cls.meta().receiver().cls()
    rec_candidates = filter(lambda m: isinstance(m, receiver_cls), react.db.machines())
    if len(rec_candidates) == 0:
        raise RuntimeError("no receiver specified for event %s" % event_name)
    elif len(rec_candidates) > 1:
        raise RuntimeError("multiple receiver candidates found for event %s: %s" % (event_name, rec_candidates))
    else:
        return rec_candidates[0]

class CallReceiversMethod(Event):
    sender              = Machine
    receiver            = Machine
    guard_method_name   = str
    handler_method_name = str

    def guard(self):
        if self.guard_method_name:
            return getattr(self.receiver, self.guard_method_name)
        return None

    def handler(self):
        return getattr(self.receiver, self.handler_method_name)()
