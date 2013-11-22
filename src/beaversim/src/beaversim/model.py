import sys
import beaversim
import beaversim.gui as gui
import thread

from react.api.model import *
from react.api.types import *

MAX_BEAVERS = 3

"""
  Records
"""
class Beaver(Record):
    name   = str
    pos_x  = int
    pos_y  = int
    lin_v  = int
    ang_v  = int

"""
  Machines
"""
class BeaverSim(Machine):
    beavers = listof(Beaver)


class RemoteCtrl(Machine):
    pass

"""
  Events
"""
class Spawn(Event):
    sender   = { "ctrl": RemoteCtrl }
    receiver = { "sim":  BeaverSim }
    name     = str
    x        = int
    y        = int

    def guard(self):
        len(self.sim.beavers) < MAX_BEAVERS

    def handler(self):
        beaver = Beaver(name=self.name, x=self.x, y=self.y)
        self.sim.beavers.append(beaver)
        
