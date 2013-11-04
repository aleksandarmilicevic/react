#!/usr/bin/env python

import sys
import rospy
import react

from react import core
from react.core import node

from react.examples.chat.chat_model import * #TODO: don't hardcode

def usage():
    return "usage:\n  rosrun react %s <machine_name>" % sys.argv[0].split("/")[-1]

if __name__ == "__main__":
    if len(sys.argv) == 2:
        machine_name = str(sys.argv[1])
        react.core.node.ReactNode(machine_name).start_node()
    else:
        print usage()
        sys.exit(1)
