#!/usr/bin/env python

import sys
import react

from react import conf
from react import core
from react.core import node
from react.utils import curry

import carsim.gui
from carsim.model import *

conf.heartbeat = True

def usage():
    return "usage:\n  rosrun carsim %s <machine_name>" % sys.argv[0].split("/")[-1]

if __name__ == "__main__":
    if len(sys.argv) == 2:
        machine_name = str(sys.argv[1])

        if machine_name in ["Master", "Car", "RemoteCtrl"]:
            file_logger = curry(conf.E_LOGGER.FILE, "%s.log" % machine_name)
            conf.cli = conf.E_THR_OPT.FALSE
            conf.log   = curry(conf._prepend, "[LOG]   ", file_logger)
            conf.debug = curry(conf._prepend, "[DEBUG] ", file_logger)
            conf.warn  = curry(conf._prepend, "[WARN]  ", file_logger)
            conf.error = curry(conf._prepend, "[ERROR] ", file_logger)
            conf.trace = conf.E_LOGGER.NULL

        # if machine_name == "Master":
        #     conf.debug = conf.E_LOGGER.NULL
        #     conf.cli = conf.E_THR_OPT.FALSE


        react.core.node.ReactMachine(machine_name).start_machine()

    else:
        print usage()
        sys.exit(1)
