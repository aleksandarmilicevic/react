import carsim
import sys
import traceback
from carsim import gui
import thread

from react import meta
from react.api.model import *
from react.api.terminals import *
from react.api.types import *
from react import conf

MAX_CARS = 5
MAX_X = 80
MAX_Y = 22
"""
  Records
"""
class CarData(Record):
    name   = str
    pos_x  = int
    pos_y  = int
    v_x    = int
    v_y    = int

"""
  Machines
"""
class Car(Machine):
    data = CarData
    closeCars = listof(CarData)

    def on_start(self):
        self.data = CarData(name="car",pos_x=0,pos_y=0,v_x=1,v_y=0)
        self.trigger(Register(sender= self, data = self.data))
        self.closeCars = []
        print('my id: %s' % self.id())

##    def every_1s(self):
##        self.data.pos_x = self.data.pos_x + self.data.v_x
##        self.data.pos_y = self.data.pos_y + self.data.v_y
##        ev = UpdatePosition(car_id=self.id(), new_x=self.data.pos_x, new_y=self.data.pos_y)
##        self.trigger(ev)

    def every_1s(self):
        # cars at intersection
        carsatintersection = []
        for car in self.closeCars:
            if (car.data.pos_x+car.data.v_x == self.data.pos_x+self.data.v_x
                and car.data.pos_y+car.data.v_y == self.data.pos_y+self.data.v_y
                and car != self):
                carsatintersection.append(car)
                
        # check of there is a headon expected collision
        for car in carsatintersection:
            if (car.data.pos_x == self.data.pos_x+2*self.data.v_x
                and car.data.pos_y == self.data.pos_y+2*self.data.v_y):

                leftfull = False
                leftupfull = False
                for car1 in self.closeCars:
                    if (car.data.pos_x+car.data.v_x == self.data.pos_x-self.data.v_y
                        and car.data.pos_y+car.data.v_y == self.data.pos_y+self.data.v_x):
                        leftfull=True
                    if (car.data.pos_x+car.data.v_x == self.data.pos_x+self.data.v_x-self.data.v_y
                        and car.data.pos_y+car.data.v_y == self.data.pos_y+self.data.v_x+self.data.v_y):
                        leftupfull=True
                if not leftfull:
                    self.data.pos_x = self.data.pos_x-self.data.v_y
                    self.data.pos_y = self.data.pos_y+self.data.v_x
                    ev = UpdatePosition(car_id=self.id(), new_x=self.data.pos_x, new_y=self.data.pos_y)
                    self.trigger(ev)
                    return None

                if not leftupfull:
                    self.data.pos_x = self.data.pos_x+self.data.v_x-self.data.v_y
                    self.data.pos_y = self.data.pos_y+self.data.v_x+self.data.v_y
                    ev = UpdatePosition(car_id=self.id(), new_x=self.data.pos_x, new_y=self.data.pos_y)
                    self.trigger(ev)
                    return None

                ev = UpdatePosition(car_id=self.id(), new_x=self.data.pos_x, new_y=self.data.pos_y)
                self.trigger(ev)
                return None

        #right of way
        for car in carsatintersection:
            if (car.data.pos_x+car.data.v_x == self.data.pos_x-self.data.v_y
                and car.data.pos_y+car.data.v_y == self.data.pos_y+self.data.v_x):

                ev = UpdatePosition(car_id=self.id(), new_x=self.data.pos_x, new_y=self.data.pos_y)
                self.trigger(ev)
                return None

        
        self.data.pos_x = self.data.pos_x + self.data.v_x
        self.data.pos_y = self.data.pos_y + self.data.v_y
        ev = UpdatePosition(car_id=self.id(), new_x=self.data.pos_x, new_y=self.data.pos_y)
        self.trigger(ev)
        return None
    
    ##TODO: unreg


class Master(Machine):
    cars = listof(Car)

    def on_start(self):
        self.cars = []
        self.term = gui.start(MAX_X, MAX_Y)

    def on_exit(self):
        self.term.stop()

    def every_1s(self):
        for car in self.cars:
            conf.log("-------------- car: %d, %d" % (car.data.pos_x, car.data.pos_y))

        self.draw_cars()
        for car in self.cars:
            closeCars = []
            for otherCar in self.cars:
                if abs(car.data.pos_x - otherCar.data.pos_x) <= 5:
                    if abs(car.data.pos_y - otherCar.data.pos_y) <= 5:
                        closeCars.append(otherCar)
            self.trigger(UpdateSensor(sender=self, receiver=car, cars=closeCars))
        # this looks wrong: the receiver is not set!
        self.trigger(UpdateRemote(cars = self.cars))

    def draw_cars(self):
        def fmap(idx):
            c = self.cars[idx]
            return (str(idx), c.data.pos_x, c.data.pos_y, idx%7 + 1)
        draw_spec = map(fmap, range(len(self.cars)))
        self.term.draw(draw_spec)

class RemoteCtrl(Machine, CursesTerminal):
    cars = listof(Car)

    def on_start(self):
        CursesTerminal.on_start(self)
        self.cnt = 0
        self.selected = None
        self.draw_menu()
        self.draw_selected()
        self.refresh()
        self.read_spin()
        self.cars = []



    def on_KEY_0(self): self.select_car(0)
    def on_KEY_1(self): self.select_car(1)
    def on_KEY_2(self): self.select_car(2)
    def on_KEY_3(self): self.select_car(3)
    def on_KEY_4(self): self.select_car(4)
    def on_KEY_5(self): self.select_car(5)

    def on_KEY_q(self):
        self.exit()

    def on_KEY_c(self):
        self.cnt = self.cnt + 1
        self.trigger(Spawn())


    def on_KEY_UP(self):
        self.trigger(ChangeSpeed(sender=self, receiver=self.cars[self.selected], dx=0,  dy=-1))
    def on_KEY_DOWN(self):
        self.trigger(ChangeSpeed(sender=self, receiver=self.cars[self.selected], dx=0,  dy=1))
    def on_KEY_LEFT(self):
        self.trigger(ChangeSpeed(sender=self, receiver=self.cars[self.selected], dx=-1, dy=0))
    def on_KEY_RIGHT(self):
        self.trigger(ChangeSpeed(sender=self, receiver=self.cars[self.selected], dx=1,  dy=0))

    def select_car(self, idx):
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
    receiver = { "car":  Car }

class ChangeSpeed(CtrlEv):
    dx       = int
    dy       = int

    def guard(self):
        pass #todo

    def handler(self):
        self.car.data.v_x = self.car.data.v_x + self.dx
        self.car.data.v_y = self.car.data.v_y + self.dy

class Register(Event):
    sender   = { "car": Car }
    receiver = { "master": Master }
    data = CarData

    def guard(self):
        return None
        #if self.data.name in [car.data.name for car in Car.all()]: return "Name taken"

    def handler(self):
        self.car.data = self.data
        self.master.cars.append(self.car)
        return self.car

class UpdateRemote(Event):
    sender   = { "master": Master }
    receiver = { "ctrl": RemoteCtrl }
    cars = listof(Car)

    def guard(self):
        pass

    def handler(self):
        self.ctrl.cars = self.cars
        return self.cars

class UpdatePosition(Event):
    sender   = { "car": Car }
    receiver = { "master": Master }

    car_id = int
    new_x = int
    new_y = int

    def guard(self):
        pass

    def handler(self):
        c = None
        for car in self.master.cars:
            conf.debug("checking car %s, data = %s" % (car, repr(car.data)))
            if car.id() == self.car_id:
                c = car;
                break
        if c is not None:
            c.data.pos_x = self.new_x
            c.data.pos_y = self.new_y
            conf.debug("updated car position: %s data = %s" % (c, repr(c.data)))
            conf.debug('my cars')
            for cc in self.master.cars:
                conf.debug(repr(cc.data))

class UpdateSensor(Event):
    sender   = { "master": Master }
    receiver = { "car": Car }
    cars = listof(CarData)

    def guard(self):
        pass

    def handler(self):
        # print("sensor info: %d nearby cars: %s" % (len(self.cars), self.cars))
        # print('my pos: %d, %d' % (self.data.pos_x, self.data.pos_y))
        self.car.closeCars = self.cars
        return self.cars
