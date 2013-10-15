#!/usr/bin/env python

import sys

import rospy
from react.srv import *
from react.msg import *
from react.examples.chat.chat_model import * #TODO: don't hardcode

def start_machine(machine_name):
    print "Requesting machine registration for machine %s" % machine_name
    reg = 'register_machine'
    rospy.wait_for_service(reg)
    try:
        reg = rospy.ServiceProxy(reg, RegisterMachineSrv)
        ans = reg(machine_name)
        print "Received response: %s" % ans
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

def usage():
    return "%s <machine_name>"%sys.argv[0]

if __name__ == "__main__":
    if len(sys.argv) == 2:
        machine_name = str(sys.argv[1])
    else:
        print usage()
        sys.exit(1)
    start_machine(machine_name)
