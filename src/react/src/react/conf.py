import react
from react.utils import curry
from react.utils import enum

@staticmethod
def _to_stdout(msg, *args): print msg % tuple(args)
@staticmethod
def _to_null(msg, *args): return None
@staticmethod
def _prepend(prefix, log_fun, msg, *args): log_fun(prefix + msg, *args)

E_THR_OPT = enum("FALSE MAIN_THR NEW_THR")
E_LOGGER  = enum(STDOUT=_to_stdout, NULL=_to_null, PREPEND=curry(_prepend))

rospy_spin = E_THR_OPT.MAIN_THR
cli        = E_THR_OPT.NEW_THR
heartbeat  = True
log        = E_LOGGER.STDOUT
debug      = E_LOGGER.STDOUT
trace      = E_LOGGER.NULL
error      = E_LOGGER.PREPEND["[ERROR] ", E_LOGGER.STDOUT]
warn       = E_LOGGER.PREPEND["[WARN] ", E_LOGGER.STDOUT]

