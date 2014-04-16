import abc
import copy
import rospy
import react
import sys
import traceback
from react import conf
from react import meta
from react import msg
from react import srv
from react.core import serialization as ser
from react.core import events
from react.core.events import *
from react.core.scheduler import Scheduler
from react.core import cli
from react.utils import curry
from react.helpers.listener_helper import ListenerHelper
import thread
import ast
import scheduler
import time

#########################################################################################

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

#########################################################################################

class ReactNode(object, ListenerHelper):
    __metaclass__ = abc.ABCMeta

    def machine(self): return None

    def cli_thr_func(self):
        command_list = []
        while True:
            s = raw_input()
            command_list.append(s)
            ans = cli.parse_and_exe(s, self)

    def forward_event_req(self, req, ev=None):
        if ev is None:
            ev = ser.deserialize_objval(req.event)

        my_machine_id = -1
        if self.machine() is not None:
            my_machine_id = self.machine().id()

        ev_receiver = ev.get_receiver()
        if ev_receiver.id() != my_machine_id:
            #TODO: this can fail
            conf.log("forwarding event %s to %s", ev, ev_receiver)
            ev_srv = rospy.ServiceProxy(event_srv_name(ev_receiver),
                                        react.srv.EventSrv)
            ev_srv(req.event)

    def trigger_whenever_events(self, ev):
        receiver = ev.get_receiver()
        receiver_cls = receiver.meta().cls()
        wh_ev_metas = react.meta.find_whenever_events(receiver_cls)
        conf.debug("found whenever events for %s machine: %s", receiver_cls, wh_ev_metas)
        if wh_ev_metas == []:
            return None
        wh_events = reduce(lambda l1, l2: l1 + l2,
                           map(lambda wh_ev_meta: wh_ev_meta.cls().instantiate(receiver),
                               wh_ev_metas))
        wh_evs = filter(lambda wh_ev: wh_ev.whenever(), wh_events)
        conf.debug("scheduling %d whenever events: %s", len(wh_evs), wh_evs)
        for wh_ev in wh_evs:
            events.call_event_service(wh_ev)

    def execute_event_req(self, req, forward=True):
        ev = ser.deserialize_objval(req.event)
        conf.debug("executing event: %s", repr(ev))
        guard_msg = ev.guard()
        status = "ok"
        if guard_msg is None:
            # if forward:
            #     self.forward_event_req(req, ev)
            try:
                self.reg_lstner()
                result = ev.handler()
                self.trigger_whenever_events(ev)
            finally:
                self.unreg_lstner()
        else:
            status = "guard failed"
            result = guard_msg
        return {
            "status": status,
            "result": ser.serialize_objref(result),
            }

    def event_handler(self, req):
        """
        Handler for the EventSrv service.
        """
        resp = self.execute_event_req(req)
        return react.srv.EventSrvResponse(**resp)

    def get_srv_handler(self, srv_name, func, log=True):
        def srv_handler(req):
            if log:
                conf.debug("*** %s *** request received", srv_name)
            try:
                resp = func(req)
                if log: conf.debug("Sending back resp:\n%s", resp)
                return resp
            except Exception as e:
                conf.error("Could not process %s handler:\n%s\n%s",
                           srv_name, e, traceback.format_exc())
                return None
        return srv_handler

#########################################################################################

class ReactCore(ReactNode):
    """
    ROS node for the ReactCore
    """

    def __init__(self):
        self._connected_nodes = dict()
        self._node_response = dict()
        self._scheduler = Scheduler()

    def start_core(self):
        rospy.init_node('reactcore')
        conf.log("initializing registration service ...")
        rospy.Service(react.core.REG_SRV_NAME,
                      react.srv.RegisterMachineSrv,
                      self.get_srv_handler("registration", self.reg_handler))
        conf.log("initializing unregistration service ...")
        rospy.Service(react.core.UNREG_SRV_NAME,
                      react.srv.UnregisterMachineSrv,
                      self.get_srv_handler("unregistration", self.unreg_handler))
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

        if conf.heartbeat:
            conf.log("scheduling check heartbeat ...")
            self._scheduler.every(5, self.check_heartbeat)

        try:
            in_thread(self.cli_thr_func, conf.cli)
            in_thread(rospy.spin, conf.rospy_spin)
        except:
            conf.error("Error: unable to start thread")

    def reg_handler(self, req):
        """
        Handler for the RegisterMachineSrv service.
        """
        mname = req.machine_name
        machine_meta = react.meta.machine(mname)
        machine_cls = machine_meta.cls()

        machine = machine_cls()
        self._connected_nodes[machine.id()] = machine
        self._node_response[machine.id()] = rospy.get_time()

        resp = {
            "this_machine": ser.serialize_objref(machine),
            "this_node_name": node_name(machine),
            "other_machines": self._get_other_machines_serialized(machine)
            }
        return react.srv.RegisterMachineSrvResponse(**resp)

    def unreg_handler(self, req):
        """
        Handler for the UnregisterMachineSrv service.
        """
        mid = req.machine.obj_id
        machine = self._connected_nodes.pop(mid, None)
        self._node_response.pop(mid)
        if machine is None:
            conf.warn("Machine %s not found in the list of connected nodes" % req.machine)
        else:
            conf.log("Machine %s disconnected" % machine)
            machine.delete()
        resp = {
            "status": "ok"
            }
        return react.srv.UnregisterMachineSrvResponse(**resp)

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
        conf.trace(req.machine)
        self._node_response[req.machine.obj_id] = rospy.get_time()
        return react.srv.HeartbeatSrvResponse(**resp)

    def check_heartbeat(self):
        conf.log("checking for unresponsive machines")
        dead_machines = []
        for machineid in self._node_response:
            if rospy.get_time() - self._node_response[machineid] > 5:
                dead_machines.append(machineid)

        for machineid in dead_machines:
            conf.log("Did not receive heartbeat from {0}. Disconnecting".format(machineid))
            self._node_response.pop(machineid)
            self._connected_nodes.pop(machineid)
            react.db.del_machine(react.db.machine(machineid))

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

    def _push_updates(self, write_accesses):
        if len(write_accesses) == 0: return
        def serref(obj): return ser.serialize_objref(obj)
        def fmap(t):     return msg.FldUpdateMsg(serref(t[1]), t[2], serref(t[3]))
        updates = map(fmap, write_accesses)
        for machine in self._connected_nodes.itervalues():
            push_srv = rospy.ServiceProxy(push_srv_name(machine), react.srv.PushSrv)
            push_srv(updates)

#########################################################################################

class ReactMachine(ReactNode):
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
        react.curr_node = self

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

    def start_machine(self):
        """
          (1) registers this machien with ReactCore (by calling
              self._register_node()).  That will initialize
              a ROS node, and also start some services to allow
              ReactCore to talk to this node directly.
        """
        try:
            self._register_node()

            rospy.init_node(self.node_name())

            if conf.heartbeat:
                conf.log("scheduling periodic hearbeat")
                self._scheduler.every(1, self._send_heartbeat)

            conf.log("initializing push service")
            rospy.Service(self.my_push_srv_name(), react.srv.PushSrv, self.push_handler)

            conf.log("initializing events service ...")
            rospy.Service(self.my_event_srv_name(),
                          react.srv.EventSrv,
                          self.get_srv_handler("event", self.event_handler))

            sys.exitfunc = self._on_exit

            if hasattr(self.machine(), "on_start"):
                self.machine().on_start()

            for every_spec in self.machine().meta().timer_events():
                self._scheduler.every(every_spec[1],
                                      curry(self._trigger_machine_method, every_spec[0]))

            in_thread(self.cli_thr_func, conf.cli)
            in_thread(rospy.spin, conf.rospy_spin)

        except rospy.ServiceException, e:
            conf.error("Service call failed: %s", e)

    def my_push_srv_name(self):  return push_srv_name(self.machine())
    def my_event_srv_name(self): return event_srv_name(self.machine())

    def _trigger_machine_method(self, method_name, *a, **kw):
        machine = self.machine()
        ev = events.CallReceiversMethod(sender              = machine,
                                        receiver            = machine,
                                        handler_method_name = method_name)
        events.call_event_service(ev)

    def _on_exit(self):
        try:
            if self.machine() is None: return
            if hasattr(self.machine(), "on_exit"):
                self.machine().on_exit()
        except Exception: pass

        try:
            unreg_srv = rospy.ServiceProxy(react.core.UNREG_SRV_NAME,
                                           react.srv.UnregisterMachineSrv)
            unreg_srv(ser.serialize_objref(self.machine()))
        except Exception: pass

    def _register_node(self):
        """
        Registers this node with ReactCore via the RegisterMachineSrv
        service.  Upon successful registration, it initializes a ROS
        node with the name received from ReactCore, and starts its own
        PushSrv service with the same name.
        """
        mname = self.machine_name()
        mcls = react.meta.machine(mname)
        if mcls is None:
            conf.fatal("Machine class %s not found", mname)
        if hasattr(mcls.cls(), "react_config"):
            getattr(mcls.cls(), "react_config")();
        conf.log("Requesting machine registration for machine %s", mname)
        rospy.wait_for_service(react.core.REG_SRV_NAME)
        reg_srv = rospy.ServiceProxy(react.core.REG_SRV_NAME, react.srv.RegisterMachineSrv)
        ans = reg_srv(mname)
        conf.debug("Received response: %s", ans)
        self._machine = ser.deserialize_objref(ans.this_machine)
        self._node_name = ans.this_node_name
        self._update_other_machines(ans.other_machines)

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
