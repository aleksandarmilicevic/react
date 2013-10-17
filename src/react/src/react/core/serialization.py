import react.msg

def deserialize_machine(record_msg):
    return None

def serialize_machine(machine):
    return react.msg.RecordMsg(machine.meta().name(), machine.id())
