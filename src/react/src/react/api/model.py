from .metamodel import *
from .record_base import *

class Record(RecordBase):
    __metaclass__ = RecordMeta

class Machine(RecordBase):
    __metaclass__ = MachineMeta

class Event(RecordBase):
    __metaclass__ = EventMeta

