import beaversim
import random
import sys
import thread
import traceback

from beaversim import gui
from react import meta
from react.api.model import *
from react.api.terminals import *
from react.api.types import *

MAX_BEAVERS = 5
MAX_X = 80
MAX_Y = 22

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
        self.term = gui.start(MAX_X, MAX_Y)

    def on_exit(self):
        self.term.stop()

    def every_100ms(self):
        self.draw_beavers()
        for beaver in self.beavers:
            beaver.pos_x = beaver.pos_x + beaver.v_x
            beaver.pos_y = beaver.pos_y + beaver.v_y

    def draw_beavers(self):
        def fmap(idx):
            b = self.beavers[idx]
            return (str(idx), b.pos_x, b.pos_y, idx%7 + 1)
        draw_spec = map(fmap, range(len(self.beavers)))
        self.term.draw(draw_spec)


class RemoteCtrl(Machine, CursesTerminal):
    def on_start(self):
        CursesTerminal.on_start(self)
        self.cnt = 0
        self.selected = None
        self.draw_menu()
        self.draw_selected()
        self.refresh()
        self.read_spin()

    def on_KEY_0(self): self.select_beaver(0)
    def on_KEY_1(self): self.select_beaver(1)
    def on_KEY_2(self): self.select_beaver(2)
    def on_KEY_3(self): self.select_beaver(3)
    def on_KEY_4(self): self.select_beaver(4)
    def on_KEY_5(self): self.select_beaver(5)

    def on_KEY_q(self):
        self.exit()

    def on_KEY_c(self):
        self.cnt = self.cnt + 1
        self.trigger(Spawn())

    def on_KEY_UP(self):
        self.trigger(ChangeSpeed(idx=self.selected, dx=0,  dy=-1))
    def on_KEY_DOWN(self):
        self.trigger(ChangeSpeed(idx=self.selected, dx=0,  dy=1))
    def on_KEY_LEFT(self):
        self.trigger(ChangeSpeed(idx=self.selected, dx=-1, dy=0))
    def on_KEY_RIGHT(self):
        self.trigger(ChangeSpeed(idx=self.selected, dx=1,  dy=0))

    def select_beaver(self, idx):
        self.selected = idx;
        self.draw_selected()
        self.refresh()

    def draw_menu(self):
        self.stdscr.addstr(0, 1, "c         - create new turtle")
        self.stdscr.addstr(1, 1, "0..5      - select turtle by index")
        self.stdscr.addstr(2, 1, "key_up    - decrease vertical velocity")
        self.stdscr.addstr(3, 1, "key_down  - increase vertical velocity")
        self.stdscr.addstr(4, 1, "key_left  - decrease horizontal velocity")
        self.stdscr.addstr(5, 1, "key_right - increase horizontal velocity")
        self.stdscr.addstr(5, 1, "q         - quit")
    def draw_selected(self):
        self.stdscr.addstr(7, 1, "selected turtle:                     ")
        self.stdscr.addstr(7, 1, "selected turtle: %s" % self.selected)
    def draw_status(self, line1, line2=""):
        self.stdscr.addstr(9, 1,  "                                                       ")
        self.stdscr.addstr(10, 1, "                                                       ")
        self.stdscr.addstr(9, 1,  str(line1))
        self.stdscr.addstr(10, 1, str(line2))
    def refresh(self):
        self.stdscr.refresh()
    def trigger(self, ev):
        try:
            resp = Machine.trigger(self, ev)
            if resp.status == "guard failed":
                self.draw_status("guard for event %s failed" % ev.meta().name(),
                                 resp.result.value)
            else:
                self.draw_status("successfully executed %s event" % ev.meta().name())
        except Exception as ex:
            self.draw_status("error executing %s event" % ev.meta().name(), str(ex))
            react.conf.error("Could not trigger %s event:\n%s",
                             ev, traceback.format_exc())
        finally:
            self.refresh()

"""
  Events
"""
class CtrlEv(Event):
    sender   = { "ctrl": RemoteCtrl }
    receiver = { "sim":  BeaverSim }

class Spawn(CtrlEv):
    name     = str

    def guard(self):
        if not len(self.sim.beavers) < MAX_BEAVERS:
            return "Too many turtles"

    def handler(self):
        beaver = Beaver(name  = self.name,
                        pos_x = random.randint(0, MAX_X),
                        pos_y = random.randint(0, MAX_Y),
                        v_x   = random.randint(-1, 1),
                        v_y   = random.randint(-1, 1))
        self.sim.beavers.append(beaver)

class ChangeSpeed(CtrlEv):
    idx      = int
    dx       = int
    dy       = int

    def guard(self):
        if not 0 <= self.idx < len(self.sim.beavers):
            return "turtle[%d] not found" % self.idx
        self._beaver = self.sim.beavers[self.idx]

    def handler(self):
        self._beaver.v_x = self._beaver.v_x + self.dx
        self._beaver.v_y = self._beaver.v_y + self.dy

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
    def handler(self):
        self.beaver.pos_x = 0
        self.beaver.v_x = -self.beaver.v_x

class RedirectBeaverR(RedirectBeaver):
    def whenever(self): return self.beaver.pos_x >= MAX_X
    def handler(self):
        self.beaver.pos_x = MAX_X-1
        self.beaver.v_x = -self.beaver.v_x

class RedirectBeaverT(RedirectBeaver):
    def whenever(self): return self.beaver.pos_y < 0
    def handler(self):
        self.beaver.pos_y = 0
        self.beaver.v_y = -self.beaver.v_y

class RedirectBeaverB(RedirectBeaver):
    def whenever(self): return self.beaver.pos_y >= MAX_Y
    def handler(self):
        self.beaver.pos_y = MAX_Y-1
        self.beaver.v_y = -self.beaver.v_y


class SetPos(CtrlEv):
    name     = str
    x        = int
    y        = int

    def guard(self):
        beavers = Beaver.where(name=self.name)
        if not beavers: return "Turtle %s not found" % self.name
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
        if not beavers: return "Trutle with name %s not found" % self.name
        self._beaver = beavers[0]

    def handler(self):
        self._beaver.v_x = self.vx
        self._beaver.v_y = self.vy

