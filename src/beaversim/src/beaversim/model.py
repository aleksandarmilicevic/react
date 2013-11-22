import sys
import beaversim
from beaversim import gui 
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
    v_x    = int
    v_y    = int

"""
  Machines
"""
class BeaverSim(Machine):
    beavers = listof(Beaver)

    def on_start(self): 
        self.gui = gui.start()
        self.beavers = [Beaver(pos_x=1,pos_y=1, v_x=0, v_y=1)]

    def every_1s(self):
        for beaver in self.beavers: 
            beaver.pos_x = beaver.pos_x + beaver.v_x
            beaver.pos_y = beaver.pos_y + beaver.v_y
        draw_spec = [(b.name, b.pos_x, b.pos_y) for b in self.beavers]
        self.gui.draw(draw_spec)

class RemoteCtrl(Machine):
    pass

"""
  Events
"""
class Spawn(Event):
    sender   = { "ctrl": RemoteCtrl }
    receiver = { "sim":  BeaverSim }
    name     = str

    def guard(self):
        self.sim.beavers.size() < MAX_BEAVERS

    def handler(self):
        beaver = Beaver(name=self.name)
        self.sim.beavers.append(beaver)
        
class SetPos(Event):
    sender   = { "ctrl": RemoteCtrl }
    receiver = { "sim":  BeaverSim }
    name     = str
    x        = int
    y        = int

    def guard(self):
        self._beaver = Beaver[name=self.name]
        if self._beaver is None: return "Beaver with name %s not found" % self.name

    def handler(self):
        self._beaver.pos_x = self.x
        self._beaver.pos_y = self.y

class SetVel(Event):
    sender   = { "ctrl": RemoteCtrl }
    receiver = { "sim":  BeaverSim }
    name     = str
    vx       = int
    vy       = int

    def guard(self):
        self._beaver = Beaver[name=self.name]
        if self._beaver is None: return "Beaver with name %s not found" % self.name

    def handler(self):
        self._beaver.v_x = self.vx
        self._beaver.v_y = self.vy
