import copy
import rospy
import react
import sys
from react import conf
from react import meta
from react import msg
from react import srv
from react.core import serialization as ser
from react.core.scheduler import Scheduler
from react.core import cli
from react.helpers.listener_helper import ListenerHelper
import thread
import ast

#########################################################################################

def node_name(machine):
    return "%s_%s" % (machine.meta().name(), machine.id())

def push_srv_name(machine):
    return "%s_%s" % (react.core.PUSH_SRV_NAME, node_name(machine))

def in_thread(fun, opt):
    if opt == conf.E_THR_OPT.FALSE:
        pass
    elif opt == conf.E_THR_OPT.NEW_THR:
        thread.start_new_thread(fun, ())
    elif opt == conf.E_THR_OPT.MAIN_THR:
        fun()
    else:
        raise StandardError("unrecognized thread option %s" % opt)

class ReactCore(object, ListenerHelper):
    """
    ROS node for the ReactCore
    """

    def __init__(self):
        self._connected_nodes = dict()

    def start_core(self):
        rospy.init_node('reactcore')
        conf.log("initializing registration service ...")
        rospy.Service(react.core.REG_SRV_NAME,
                      react.srv.RegisterMachineSrv,
                      self.get_srv_handler("registration", self.reg_handler))
        conf.log("initializing events service ...")
        rospy.Service(react.core.EVENT_SRV_NAME,
                      react.srv.EventSrv,
                      self.get_srv_handler("event", self.event_handler))
        conf.log("initializing node discovery service ...")
        rospy.Service(react.core.NODE_DISCOVERY_SRV_NAME,
                      react.srv.NodeDiscoverySrv,
                      self.get_srv_handler("discover", self.node_discovery_handler))
        conf.log("initializing heartbeat service ...")
        rospy.Service(react.core.HEARTBEAT_SRV_NAME,
                      react.srv.HeartbeatSrv,
                      self.get_srv_handler("heartbeat", self.heartbeat_handler, False))

        try:
            in_thread(self.commandInterface, conf.cli)
            in_thread(rospy.spin, conf.rospy_spin)
        except:
            conf.error("Error: unable to start thread")

    def commandInterface(self):
        while True:
            s = raw_input()
            ans = cli.parse_and_exe(s, self)
            if ans is not None:
                conf.debug("Received response: %s", ans)

    def event_handler(self, req):
        """
        Handler for the EventSrv service.
        """
        ev = ser.deserialize_objval(req.event)
        guard_msg = ev.guard()
        status = "ok"
        if guard_msg is None:
            try:
                self.reg_lstner()
                result = ev.handler()
            finally:
                self.unreg_lstner()
        else:
            status = "guard failed"
            result = guard_msg
        self._push_updates()
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

        machine = machine_cls()
        self._connected_nodes[machine.id()] = machine

        resp = {
            "this_machine": ser.serialize_objref(machine),
            "this_node_name": node_name(machine),
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

    def heartbeat_handler(self, req):
        """
        Handler for the HeartbeatSrv service.
        """
        conf.trace("Received heartbeat from %s", req.machine)
        resp = {
            "ok": True
            }
        return react.srv.HeartbeatSrvResponse(**resp)

    def get_srv_handler(self, srv_name, func, log=True):
        def srv_handler(req):
            if log: conf.debug("*** %s *** request received\n%s", srv_name, req)
            resp = func(req)
            if log: conf.debug("Sending back resp:\n%s", resp)
            if log: conf.debug("--------------------------\n")
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

    def _push_updates(self):
        wa = self.write_accesses()
        if len(wa) == 0: return
        def serref(obj): return ser.serialize_objref(obj)
        def fmap(t):     return msg.FldUpdateMsg(serref(t[1]), t[2], serref(t[3]))
        updates = map(fmap, wa)
        for machine in self._connected_nodes.itervalues():
            push_srv = rospy.ServiceProxy(push_srv_name(machine), react.srv.PushSrv)
            push_srv(updates)

#########################################################################################

class ReactNode(object):
    """
    ROS node for React machines
    """

    def __init__(self, machine_name):
        """ @param machine_name: name of the corresponding machine """
        self._machine_name = machine_name
        self._machine = None
        self._node_name = None
        self._other_machines = list()
        self._scheduler = Scheduler()

    def machine_name(self):   return self._machine_name
    def machine(self):        return self._machine
    def node_name(self):      return self._node_name
    def other_machines(self): return self._other_machines

    def push_handler(self, req):
        updates = req.field_updates
        changed = True
        while len(updates) > 0 and changed:
            changed = False
            for fld_update in copy.copy(updates):
                obj = ser.deserialize_existing(fld_update.target)
                fname = fld_update.field_name
                if obj is not None:
                    changed = True
                    updates.remove(fld_update)
                    
                    val = ser.deserialize_objref(fld_update.field_value)
                    obj.set_field(fname, val)
                    conf.debug("updated %s.%s = %s", obj, fname, val)
        return react.srv.PushSrvResponse("ok")

    def commandInterface(self):
        commandList = []
        while True:
            s = raw_input()
            commandList.append(s)
            ans = cli.parse_and_exe(s, self)
        curses.endwin()

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
            in_thread(self.commandInterface, conf.cli)
            in_thread(rospy.spin, conf.rospy_spin)

        except rospy.ServiceException, e:
            conf.error("Service call failed: %s", e)

    def my_push_srv_name(self):
        return push_srv_name(self.machine())

    def _register_node(self):
        """
        Registers this node with ReactCore via the RegisterMachineSrv
        service.  Upon successful registration, it initializes a ROS
        node with the name received from ReactCore, and starts its own
        PushSrv service with the same name.
        """
        mname = self.machine_name()
        conf.log("Requesting machine registration for machine %s", mname)
        rospy.wait_for_service(react.core.REG_SRV_NAME)
        reg_srv = rospy.ServiceProxy(react.core.REG_SRV_NAME, react.srv.RegisterMachineSrv)
        ans = reg_srv(mname)
        conf.debug("Received response: %s", ans)
        self._machine = ser.deserialize_objref(ans.this_machine)
        self._node_name = ans.this_node_name
        self._update_other_machines(ans.other_machines)

        rospy.init_node(self.node_name())
        if conf.heartbeat: self._scheduler.every(1, self._send_heartbeat)

        conf.log("initializing push service")
        rospy.Service(self.my_push_srv_name(), react.srv.PushSrv, self.push_handler)

        if hasattr(self.machine(), "on_exit"):
            sys.exitfunc = self.machine().on_exit

        if hasattr(self.machine(), "on_start"):
            self.machine().on_start()

        for every_event_spec in self.machine().meta().timer_events():
            self._scheduler.every(every_event_spec[1], getattr(self.machine(), every_event_spec[0]))

    def _send_heartbeat(self):
        """
        Simply send a heartbeat to ReactCore to indicate that this
        node is still alive.
        """
        conf.trace("Sending heartbeat")
        hb_srv = rospy.ServiceProxy(react.core.HEARTBEAT_SRV_NAME, react.srv.HeartbeatSrv)
        hb_srv(ser.serialize_objref(self.machine()))

    def _update_other_machines(self, machine_msgs):
        """
        Takes a list of ObjRefMsg object, deserializes them, and
        updates the `_other_machines' field of self.

        @param machine_msgs: list<ObjRefMsg>; other machines
        """
        self._other_machines = map(lambda m: ser.deserialize_objref(m), machine_msgs)
