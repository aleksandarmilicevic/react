#!/usr/bin/env python

import rospy

import react
from react import srv
from react import core
from react import meta
from react.core import serialization as ser
from std_msgs.msg import String

from react.examples.chat.chat_model import * #TODO: don't hardcode

# int -> str
# maps machine id to a channel name to be used to send messages to that machine
connected_nodes = dict()

def event_handler(req):
    #TODO
    return react.srv.EventSrvResponse("ok")

def reg_handler(req):
    mname = req.machine_name

    #TODO
    print "registration request"
    print "  machine name: %s" % mname

    print "Resolving machine name %s" % mname
    machine_meta = react.meta.machine(mname)
    machine_cls = machine_meta.cls()

    print "Creating new machine instance" 
    machine = machine_cls()
    node_name = "%s_%s" % (machine.meta().name(), machine.id())
    connected_nodes[machine.id()] = node_name
    
    resp = {
        "machine": ser.serialize_objref(machine), 
        "node_name": node_name
        }
    print "Sending back resp: %s" % resp
    return react.srv.RegisterMachineSrvResponse(**resp)

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
