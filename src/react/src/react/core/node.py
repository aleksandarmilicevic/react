import sys
import rospy
import react
from react.core import serialization as ser
from react import srv
from react import msg
from react import meta

class ReactNode(object):
    def __init__(self, machine_name):
        """ @param machine_name: name of the corresponding machine """
        self._machine_name = machine_name
        self._machine = None

    def machine_name(self): return self._machine_name
    def machine(self):      return self._machine

    def push_handler(self, req):
        print "received: %s" % req
        return react.srv.PushSrvResponse("ok")

    def start_node(self):
        mname = self.machine_name()
        print "Requesting machine registration for machine %s" % mname
        rospy.wait_for_service(react.core.REG_SRV_NAME)
        try:
            reg = rospy.ServiceProxy(react.core.REG_SRV_NAME, react.srv.RegisterMachineSrv)
            ans = reg(mname)
            print "Received response: %s" % ans
            self._machine = ser.deserialize_objref(ans.machine)
            print "Deserialized into %s" % self.machine()

            rospy.init_node(ans.node_name)
            print "initializing push service"
            rospy.Service(react.core.PUSH_SRV_NAME, react.srv.PushSrv, self.push_handler)

            # send register event (should be triggered by the user)
            reg_ev_cls = meta.event("Register").cls()
            ev = reg_ev_cls()
            ev.name = "aleks"
            ev_service = rospy.ServiceProxy(react.core.EVENT_SRV_NAME, react.srv.EventSrv)
            ev_msg = ser.serialize_objval(ev)
            ans = ev_service(ev_msg)
            print "Received response from EventSrv: %s" % ans

            # TODO: read commands from kbd
            rospy.spin()

        except rospy.ServiceException, e:
            print "Service call failed: %s" % e

