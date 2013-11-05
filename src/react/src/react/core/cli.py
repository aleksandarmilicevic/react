import re
import rospy
import react

from react.core import serialization as ser
from react import meta
from react import srv
from react import msg

cmd_regex = re.compile(r"(?P<cmd>\w+)(\s+(?P<name>\w+))?(\((?P<params>.*)\))?(\s+to\s+@(?P<receiver_id>\d+))?\s*$")

def parse(cmd_str):
    """ @param cmd_str [string]: command to execute """
    m = cmd_regex.match(cmd_str)
    if m is None: return None
    cmd = m.group("cmd")
    name = m.group("name")
    params = dict()
    params_str = m.group("params")
    if params_str is not None:
        #TODO: unsafe eval
        params = eval('dict(%s)' % params_str)
    to = m.group("receiver_id")
    if to is not None: to = int(to)
    return (cmd, name, params, to)

def exe_cmd(cmd_tuple, react_node):
    """
    @param cmd_tuple[0] [string]    : command
    @param cmd_tuple[1] [string]    : name
    @param cmd_tuple[2] [dict]      : parameters
    @param react_node   [ReactNode] : acting node
    """
    if cmd_tuple[0] == "trigger":
        ev_params = cmd_tuple[2]
        ev_params.update({"sender": react_node.machine()})
        return trigger_event(cmd_tuple[1], **ev_params)
    elif cmd_tuple[0] == "db":
        print "records: "
        for record in react.db._records().values():
            print "  " + repr(record)
        print ""
        print "machines: "
        for machine in react.db._machines().values():
            print "  " + repr(machine)
    else:
        raise RuntimeException("unknown command: %s" % cmd[0])

def parse_and_exe(cmd_str, react_node):
    cmd = parse(cmd_str)
    return exe_cmd(cmd, react_node)

def trigger_event(event_name, **event_params):
    ev_cls = meta.event(event_name).cls()
    ev = ev_cls(**event_params)

    ev_service = rospy.ServiceProxy(react.core.EVENT_SRV_NAME, react.srv.EventSrv)
    ev_msg = ser.serialize_objval(ev)
    return ev_service(ev_msg)
