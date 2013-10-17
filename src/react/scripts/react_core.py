#!/usr/bin/env python

import rospy

import react
from react import srv
from react import core
from react import meta
from react.core import serialization as ser
from std_msgs.msg import String

from react.examples.chat.chat_model import * #TODO: don't hardcode

def event_handler(req):
    #TODO
    return react.srv.EventSrvResponse("ok")

def reg_handler(req):
    mname = req.machine_name

    #TODO
    print "registration request"
    print "  machine name: %s" % mname

    print "Resolving machine name %s" % mname
    machine_meta = react.meta.find_machine(mname)
    machine_cls = machine_meta.cls()

    print "Creating new machine instance" 
    machine = machine_cls()

    print "  machine id: %s" % machine.id()
    
    resp = ser.serialize_machine(machine)
    print "Sending back resp: %s" % resp
    return react.srv.RegisterMachineSrvResponse(resp)

def reactcore():
    rospy.init_node('reactcore')
    print "initializing registration service ..."
    rospy.Service(react.core.REG_SRV_NAME, react.srv.RegisterMachineSrv, reg_handler)
    print "initializing events service ..."
    rospy.Service(react.core.EVENT_SRV_NAME, react.srv.EventSrv, event_handler)
    print "done"
    rospy.spin()

if __name__ == "__main__":
    reactcore()
