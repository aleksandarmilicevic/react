import sys
import rospy
import react
from react.core import serialization as ser
from react import srv
from react import msg
from react import meta
from react.core import cli
import thread
import ast

class ReactCore(object):
    def __init__(self):
        self._connected_nodes = dict()

    def start_core(self):
        rospy.init_node('reactcore')
        print "initializing registration service ..."
        rospy.Service(react.core.REG_SRV_NAME,
                      react.srv.RegisterMachineSrv,
                      self.get_srv_handler("registration", self.reg_handler))
        print "initializing events service ..."
        rospy.Service(react.core.EVENT_SRV_NAME,
                      react.srv.EventSrv,
                      self.get_srv_handler("event", self.event_handler))
        print "initializing node discovery service ..."
        rospy.Service(react.core.NODE_DISCOVERY_SRV_NAME,
                      react.srv.NodeDiscoverySrv,
                      self.get_srv_handler("discover", self.node_discovery_handler))
        try:
            thread.start_new_thread(self.commandInterface,())
            thread.start_new_thread(rospy.spin(),())
        except:
            print "Error: unable to start thread"

    def commandInterface(self):
        while True:
            s = raw_input()
            ans = cli.parse_and_exe(s, self)
            if ans is not None:
                print "Received response: %s" % ans

    def event_handler(self, req):
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

    def reg_handler(self, req):
        """
        Handler for the RegisterMachineSrv service.
        """
        mname = req.machine_name
        machine_meta = react.meta.machine(mname)
        machine_cls = machine_meta.cls()

        print "Creating new machine instance"
        machine = machine_cls()
        node_name = "%s_%s" % (machine.meta().name(), machine.id())
        self._connected_nodes[machine.id()] = node_name

        resp = {
            "this_machine": ser.serialize_objref(machine),
            "this_node_name": node_name,
            "other_machines": self._get_other_machines_serialized(machine)
            }
        return react.srv.RegisterMachineSrvResponse(**resp)

    def node_discovery_handler(self, req):
        """
        Handler for the NodeDiscoverSrv service.
        """
        resp = {
            "other_machines": self._get_other_machines_serialized(req.client_machine.obj_id)
            }
        return react.srv.NodeDiscoverySrvResponse(**resp)

    def get_srv_handler(self, srv_name, func):
        def srv_handler(req):
            print "*** %s *** request received\n%s" % (srv_name, req)
            resp = func(req)
            print "Sending back resp:\n%s" % resp
            print "--------------------------\n"
            return resp
        return srv_handler

    def _get_other_machines(self, this_machine):
        """
        Returns a list of connected machines other than `this_machine'

        @param this_machine: Machine; machine to omit from the returned list
        @return list<Machine>;        list of other connected machines
        """
        if isinstance(this_machine, int): this_machine_id = this_machine
        else:                             this_machine_id = this_machine.id()
        node_ids = self._connected_nodes.keys()
        if this_machine_id in node_ids: node_ids.remove(this_machine_id)
        return map(lambda id: react.db.machine(id), node_ids)

    def _get_other_machines_serialized(self, this_machine):
        """
        Returns a list of connected machines other than `this_machine'
        serialized to ObjRefMsg objects.

        @param this_machine: Machine; machine to omit from the returned list
        @return list<ObjRefMsg>;      list of other connected machines
        """
        return map(lambda m: ser.serialize_objref(m), self._get_other_machines(this_machine))

#########################################################################################

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

    def commandInterface(self):
        while True:
            s = raw_input()
            ans = cli.parse_and_exe(s, self)
            if ans is not None:
                print "Received response: %s" % ans

    def start_node(self):
        """
          (1) registers this machien with ReactCore (by calling
              self._register_node()).  That will initialize
              a ROS node, and also start some services to allow
              ReactCore to talk to this node directly.

          (2) creates and triggers the Register event from the Chat
              system model.
        """
        try:
            self._register_node()

            # !!!!!! THIS IS JUST AN EXAMPLE, NOT A GENERIC NODE BEHAVIOR !!!!!!!
            # pick any connected Server node and trigger Register event
            servers = filter(lambda m: m.meta().name() == "Server", self.other_machines())
            if len(servers) == 0:
                print "*** No connected servers found."
            else:
                pass
                #self._trigger_event("Register", receiver=servers[0], name="aleks")
            # !!!!!! ==================================================== !!!!!!!

            # TODO: allow command imputs from kbd
            thread.start_new_thread(self.commandInterface,())
            thread.start_new_thread(rospy.spin(),())

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
