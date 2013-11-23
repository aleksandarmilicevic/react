import react
import sys
from react.utils import curry
from react.utils import enum

@staticmethod
def _to_stdout(msg, *args): print msg % tuple(args)
@staticmethod
def _to_null(msg, *args): return None
@staticmethod
def _to_file(fname, msg, *args):
    with open(fname, "a") as log_file:
        log_file.write(msg % tuple(args))
        log_file.write("\n")

def _prepend(prefix, log_fun, msg, *args): log_fun(prefix + msg, *args)
def _compose(f1, f2, msg, *args): f1(msg, *args); f2(msg, *args)

E_THR_OPT = enum("FALSE MAIN_THR NEW_THR")
E_LOGGER  = enum(STDOUT  = _to_stdout,
                 NULL    = _to_null,
                 FILE    = _to_file)

rospy_spin = E_THR_OPT.MAIN_THR
cli        = E_THR_OPT.NEW_THR
heartbeat  = True
log        = E_LOGGER.STDOUT
debug      = E_LOGGER.STDOUT
trace      = E_LOGGER.NULL
error      = curry(_prepend)["[ERROR] ", E_LOGGER.STDOUT]
warn       = curry(_prepend)["[WARN] ", E_LOGGER.STDOUT]
fatal      = curry(_compose)[error, lambda *a: sys.exit(1)]
