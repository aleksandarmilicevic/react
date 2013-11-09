import sys
import rospy
import react
from react.core import serialization as ser
from react import srv
from react import msg
from react import meta 
from react.core import cli
import thread

class Scheduler(object):
    def __init__(self):
        pass

    def every(self, millis, task):
        """
        Registers the given callable `task' to be called (invoked)
        every `millis' milliseconds.

        @param millis [int]      - time interval
        @param task   [Callable] - timer task to call every `millis' milliseconds
        """
        pass

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
        pass

    def unregister(self, task):
        """
        Removes the given timer task from this scheduler so that is is
        not called in the future.
        """
        pass
