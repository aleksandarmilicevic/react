#!/usr/bin/env python

from ros_tut.srv import *
import rospy

def handler(req):
    print "Returning [%s + %s = %s]" % (req.a, req.b, (req.a + req.b))
    return AddTwoIntsResponse(req.a + req.b)

def server():
    rospy.init_node('add_two_ints_server')
    s = rospy.Service('add_two_ints', AddTwoInts, handler)
    print "Readey to add two ints."
    rospy.spin()

if __name__ == "__main__":
    server()
