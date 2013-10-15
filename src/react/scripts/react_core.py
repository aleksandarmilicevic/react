#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from react.api.model import *
from react.msg import *
from react.srv import *

from react.examples.chat.chat_model import * #TODO: don't hardcode

def event_handler(req):
    #TODO
    return EventSrvResponse("ok")

def registration_handler(req):
    #TODO
    print "registration request"
    print "  machine name: %s" % req.machine_name

    print "Resolving machine name %s" % req.machine_name
    machine_cls = eval(req.machine_name) #TODO don't use eval!

    print "Creating new machine instancd" 
    machine = machine_cls()

    print "  machine id: %s" % machine.id()

    resp = RecordMsg(machine.meta().name(), machine.id())
    print "Sending back resp: %s" % resp
    return RegisterMachineSrvResponse(resp)

def reactcore():
    rospy.init_node('reactcore')
    print "initializing registration service ..."
    rospy.Service('register_machine', RegisterMachineSrv, registration_handler)
    print "initializing events service ..."
    rospy.Service('events', EventSrv, event_handler)
    print "done"
    rospy.spin()

if __name__ == "__main__":
    reactcore()
