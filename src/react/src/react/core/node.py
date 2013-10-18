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
        self._node_name = None
        self._other_machines = list()

    def machine_name(self):   return self._machine_name
    def machine(self):        return self._machine
    def node_name(self):      return self._node_name
    def other_machines(self): return self._other_machines

    def push_handler(self, req):
        print "received: %s" % req
        return react.srv.PushSrvResponse("ok")

    def start_node(self):
        try:
            self._register_node()

            # send register event (should be triggered by the user)
            reg_ev_cls = meta.event("Register").cls()
            ev = reg_ev_cls(
                sender = self.machine(),
                name = "aleks"
                )
            ev.name = "aleks"
            ev_service = rospy.ServiceProxy(react.core.EVENT_SRV_NAME, react.srv.EventSrv)
            ev_msg = ser.serialize_objval(ev)
            ans = ev_service(ev_msg)
            print "Received response from EventSrv: %s" % ans

            # TODO: read commands from kbd
            rospy.spin()

        except rospy.ServiceException, e:
            print "Service call failed: %s" % e


    def _register_node(self):
        """
        Registers this node with ReactCore via the RegisterMachineSrv
        service.  Upon successful registration, it initializes a ROS
        node with the name received from ReactCore, and starts its own
        PushSrv service with the same name.
        """
        mname = self.machine_name()
        print "Requesting machine registration for machine %s" % mname
        rospy.wait_for_service(react.core.REG_SRV_NAME)
        reg_srv = rospy.ServiceProxy(react.core.REG_SRV_NAME, react.srv.RegisterMachineSrv)
        ans = reg_srv(mname)
        print "Received response: %s" % ans
        self._machine = ser.deserialize_objref(ans.this_machine)
        self._node_name = ans.this_node_name
        self._update_other_machines(ans.other_machines)

        rospy.init_node(self.node_name())
        print "initializing push service"
        rospy.Service(react.core.PUSH_SRV_NAME, react.srv.PushSrv, self.push_handler)

    def _update_other_machines(self, machine_msgs):
        """
        Takes a list of ObjRefMsg object, deserializes them, and
        updates the `_other_machines' field of self. 

        @param machine_msgs: list<ObjRefMsg>; other machines
        """
        self._other_machines = map(lambda m: ser.deserialize_objref(m), machine_msgs)
