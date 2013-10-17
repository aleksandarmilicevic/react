import sys
import rospy
import react
from react.core import serialization as ser
from react import srv
from react import msg

class ReactNode(object):
    def __init__(self, machine_name):
        """ @param machine_name: name of the corresponding machine """
        self._machine_name = machine_name
        self._machine = None

    def machine_name(self): return self._machine_name
    def machine(self):      return self._machine

    def start_node(self):
        mname = self.machine_name()
        print "Requesting machine registration for machine %s" % mname
        rospy.wait_for_service(react.core.REG_SRV_NAME)
        try:
            reg = rospy.ServiceProxy(react.core.REG_SRV_NAME, react.srv.RegisterMachineSrv)
            ans = reg(mname)
            print "Received response: %s" % ans
            self._machine = ser.deserialize_machine(ans)
            print "Deserialized into %s" % self.machine()
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e

