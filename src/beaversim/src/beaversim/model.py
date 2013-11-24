import sys
import beaversim
from beaversim import gui
import thread

from react import meta
from react.api.model import *
from react.api.terminals import *
from react.api.types import *

MAX_BEAVERS = 3
MAX_X = 80
MAX_Y = 25

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
class BeaverSim(Machine, CursesTerminal):
    beavers = listof(Beaver)

    def on_start(self):
        self.term = gui.start()

    def on_exit(self):
        self.term.stop()

    def every_1s(self):
        for beaver in self.beavers:
            beaver.pos_x = beaver.pos_x + beaver.v_x
            beaver.pos_y = beaver.pos_y + beaver.v_y
        draw_spec = [(b.name, b.pos_x, b.pos_y, 1) for b in self.beavers]
        self.term.draw(draw_spec)

class RemoteCtrl(Machine):
    pass

"""
  Events
"""
class CtrlEv(Event):
    sender   = { "ctrl": RemoteCtrl }
    receiver = { "sim":  BeaverSim }


class Spawn(CtrlEv):
    name     = str

    def guard(self):
        len(self.sim.beavers) < MAX_BEAVERS

    def handler(self):
        beaver = Beaver(name=self.name, pos_x=0, pos_y=0, v_x=1, v_y=0)
        self.sim.beavers.append(beaver)

class SetPos(CtrlEv):
    name     = str
    x        = int
    y        = int

    def guard(self):
        beavers = Beaver.where(name=self.name)
        if not beavers: return "Beaver %s not found" % self.name
        self._beaver = beavers[0]

    def handler(self):
        self._beaver.pos_x = self.x
        self._beaver.pos_y = self.y

class SetVel(CtrlEv):
    name     = str
    vx       = int
    vy       = int

    def guard(self):
        beavers = Beaver.where(name=self.name)
        if not beavers: return "Beaver with name %s not found" % self.name
        self._beaver = beavers[0]

    def handler(self):
        self._beaver.v_x = self.vx
        self._beaver.v_y = self.vy

# ----------------------------------------------------
# Redirect beavers whenever outside the bounding box

class RedirectBeaver(WheneverEvent):
    receiver = { "sim": BeaverSim }
    beaver   = Beaver

    @classmethod
    def instantiate(cls, rec):
        return map(lambda b: cls(beaver=b, receiver=rec), rec.beavers)

class RedirectBeaverL(RedirectBeaver):
    def whenever(self): return self.beaver.pos_x < 0
    def handler(self):  self.beaver.pos_x = 0; self.beaver.v_x = -self.beaver.v_x

class RedirectBeaverR(RedirectBeaver):
    def whenever(self): return self.beaver.pos_x > MAX_X
    def handler(self):  self.beaver.pos_x = MAX_X; self.beaver.v_x = -self.beaver.v_x

class RedirectBeaverT(RedirectBeaver):
    def whenever(self): return self.beaver.pos_y < 0
    def handler(self):  self.beaver.pos_y = 0; self.beaver.v_y = -self.beaver.v_y

class RedirectBeaverB(RedirectBeaver):
    def whenever(self): return self.beaver.pos_y > MAX_Y
    def handler(self):  self.beaver.pos_y = MAX_Y; self.beaver.v_y = -self.beaver.v_y
