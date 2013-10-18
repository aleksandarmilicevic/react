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

def get_srv_handler(srv_name, func):
    def srv_handler(req):
        print "*** %s *** request received\n%s" % (srv_name, req)
        resp = func(req)
        print "Sending back resp:\n%s" % resp
        print "--------------------------\n"
        return resp
    return srv_handler

def event_handler(req):
    """
    Handler for the EventSrv service.
    """
    ev = ser.deserialize_objval(req.event)
    guard_msg = ev.guard()
    status = "ok"
    if guard_msg is None:
        result = ev.handler()
    else:
        status = "guard failed"
        result = guard_msg
    resp = {
        "status": status, 
        "result": ser.serialize_objref(result)
        }
    return react.srv.EventSrvResponse(**resp)

def reg_handler(req):
    """
    Handler for the RegisterMachineSrv service.
    """
    mname = req.machine_name
    machine_meta = react.meta.machine(mname)
    machine_cls = machine_meta.cls()

    print "Creating new machine instance" 
    machine = machine_cls()
    node_name = "%s_%s" % (machine.meta().name(), machine.id())
    connected_nodes[machine.id()] = node_name
    
    resp = {
        "this_machine": ser.serialize_objref(machine), 
        "this_node_name": node_name, 
        "other_machines": _get_other_machines_serialized(machine)
        }
    return react.srv.RegisterMachineSrvResponse(**resp)

def node_discovery_handler(req):
    """
    Handler for the NodeDiscoverSrv service.
    """
    resp = { "other_machines": _get_other_machines_serialized(req.client_machine.obj_id) }
    return react.srv.NodeDiscoverySrvResponse(**resp)

def reactcore():
    rospy.init_node('reactcore')
    print "initializing registration service ..."
    rospy.Service(react.core.REG_SRV_NAME, 
                  react.srv.RegisterMachineSrv, 
                  get_srv_handler("registration", reg_handler))
    print "initializing events service ..."
    rospy.Service(react.core.EVENT_SRV_NAME, 
                  react.srv.EventSrv, 
                  get_srv_handler("event", event_handler))
    print "initializing node discovery service ..."
    rospy.Service(react.core.NODE_DISCOVERY_SRV_NAME, 
                  react.srv.NodeDiscoverySrv, 
                  get_srv_handler("discover", node_discovery_handler))
    print "done"
    # TODO: allow command imputs from keyboard
    rospy.spin()

def _get_other_machines(this_machine):
    """
    Returns a list of connected machines other than `this_machine'

    @param this_machine: Machine; machine to omit from the returned list
    @return list<Machine>;        list of other connected machines
    """
    if isinstance(this_machine, int): this_machine_id = this_machine 
    else:                             this_machine_id = this_machine.id()
    node_ids = connected_nodes.keys()
    if this_machine_id in node_ids: node_ids.remove(this_machine_id)
    return map(lambda id: react.db.machine(id), node_ids)

def _get_other_machines_serialized(this_machine):
    """
    Returns a list of connected machines other than `this_machine'
    serialized to ObjRefMsg objects.

    @param this_machine: Machine; machine to omit from the returned list
    @return list<ObjRefMsg>;      list of other connected machines
    """
    return map(lambda m: ser.serialize_objref(m), _get_other_machines(this_machine))

if __name__ == "__main__":
    reactcore()
