import rospy
import react
from react import meta
from react import srv
from react import msg
from react.core import serialization as ser
from react.api.model import *

def node_name(machine):
    return "%s_%s" % (machine.meta().name(), machine.id())

def event_srv_name(machine):
    return "%s_%s" % (react.core.EVENT_SRV_NAME, node_name(machine))

def call_event_service(ev):
    ev_service = rospy.ServiceProxy(event_srv_name(ev.get_receiver()), react.srv.EventSrv)
    # ev_service = rospy.ServiceProxy(react.core.EVENT_SRV_NAME, react.srv.EventSrv)
    ev_msg = ser.serialize_objval(ev)
    return ev_service(ev_msg)

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
