import re
import rospy
import react

from react.core import serialization as ser
from react.core import events
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
    if cmd_tuple[0] in ["trigger", "send"]:
        ev_params = cmd_tuple[2]
        rec_id = cmd_tuple[3]
        if rec_id is not None:
            rec = react.db.machine(rec_id)
        else:
            rec = None
        ev_params.update({"sender": react_node.machine(), "receiver": rec})
        return trigger_event(cmd_tuple[1], **ev_params)
    elif cmd_tuple[0] == "db":
        print "records: "
        for record in react.db.records():
            print "  " + repr(record)
        print ""
        print "machines: "
        for machine in react.db.machines():
            print "  " + repr(machine)
    elif cmd_tuple[0] == "hb" and callable(getattr(react_node, "_send_heartbeat", None)):
        react_node._send_heartbeat()
    else:
        cli_error("unknown command: %s" % cmd_tuple[0])
        # raise RuntimeError("unknown command: %s" % cmd_tuple[0])

def parse_and_exe(cmd_str, react_node):
    if not cmd_str: return
    cmd = parse(cmd_str)
    if cmd is None:
        cli_error("invalid syntax: %s" % cmd_str)
    else:
        return exe_cmd(cmd, react_node)

def cli_error(msg):
    print("CLI ERROR: %s" % msg)

def trigger_event(event_name, **event_params):
    ev_cls = meta.event(event_name).cls()
    if event_params.get("receiver") is None:
        rec = events.find_implicit_receiver(ev_cls)
        print "Using implicit receiver: %s" % rec
        event_params["receiver"] = rec
    ev = ev_cls(**event_params)
    events.call_event_service(ev)
