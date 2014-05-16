#!/usr/bin/env python

import sys
import react

from react import conf
from react import core
from react.core import node

import beaversim.gui
from beaversim.model import *

#conf.debug = conf.E_LOGGER.NULL
conf.heartbeat = True

def usage():
    return "usage:\n  rosrun beaversim %s <machine_name>" % sys.argv[0].split("/")[-1]

if __name__ == "__main__":
    if len(sys.argv) == 2:
        machine_name = str(sys.argv[1])

        file_logger = curry(conf.E_LOGGER.FILE, "%s.log" % machine_name)
        conf.cli = conf.E_THR_OPT.FALSE
        conf.log   = curry(conf._prepend, "[LOG]   ", file_logger)
        conf.debug = curry(conf._prepend, "[DEBUG] ", file_logger)
        conf.warn  = curry(conf._prepend, "[WARN]  ", file_logger)
        conf.error = curry(conf._prepend, "[ERROR] ", file_logger)
        conf.trace = curry(conf._prepend, "[TRACE] ", file_logger)

        react.core.node.ReactMachine(machine_name).start_machine()


        # if machine_name == "BeaverSim":
        #     from PyQt4 import QtGui
        #     sys.exit(gui.BeaverQtApp.exec_())

        # if machine_name == "BeaverSim":
        #     import pygtk
        #     pygtk.require('2.0')
        #     import gtk
        #     gtk.main()


    else:
        print usage()
        sys.exit(1)
