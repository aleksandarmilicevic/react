import sys
import rospy
import react
from react.core import serialization as ser
from react import srv
from react import msg
from react import meta 
from react.core import cli
import thread
import time

class Scheduler(object):
    def __init__(self):
        self.timers = []                    
    
    def every(self, sec, task):
        """
        Registers the given callable `task' to be called (invoked)
        every `sec' seconds.

        @param sec [int]      - time interval
        @param task   [Callable] - timer task to call every `millis' milliseconds
        """
        def callback(event):
            task()

        timer = rospy.Timer(rospy.Duration(sec),callback)
        self.timers.append((task,timer))
            
    
    def at(self, hour, minute, second, task):
        """
        Calls `task' whenever 
          current_hour in hour and
          current_minute in minute and
          current_second in second

        @param hour   [list]     - the hour pattern
        @param minute [list]     - the minute pattern
        @param second [list]     - the second pattern
        @param task   [Callable] - timer task to call whenever the
                                   current time matches the given time pattern
        """
        sec = 60*60*hour + 60*minute + second
        current = self.getCurrentTime()
        currentSec = 60*60*current[0]+60*current[1]+current[2]
        def callback(event):
            task()
            self.every(24*60*60,task)
            
        if sec >= currentSec:
            timer = rospy.Timer(rospy.Duration(sec-currentSec),callback)
        else:
            timer = rospy.Timer(rospy.Duration(24*60*60-currentSec+sec),callback, oneshot=True)
        self.timers.append((task,timer))
    
    def getCurrentTime(self):
        timeStr = time.asctime(time.localtime())
        sec = timeStr[-7:-5]
        minute = timeStr[-10:-8]
        hour = timeStr[-13:-11]
        return [int(hour),int(minute),int(sec)]

    def unregister(self, task):
        """
        Removes the given timer task from this scheduler so that it is
        not called in the future.
        """
        for taskTimer in self.timers:
            if taskTimer[0] == task:
                taskTimer[1].shutdown()
