#!/usr/bin/env python

import sys
import react

from react import core
from react.core import node

import beaversim.gui
from beaversim.model import *


def usage():
    return "usage:\n  rosrun beaversim %s <machine_name>" % sys.argv[0].split("/")[-1]

if __name__ == "__main__":
    if len(sys.argv) == 2:
        machine_name = str(sys.argv[1])
        react.core.node.ReactNode(machine_name).start_node()

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
