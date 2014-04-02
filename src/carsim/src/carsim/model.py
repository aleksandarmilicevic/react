import carsim
import sys
import traceback
from carsim import gui
import thread

from react import meta
from react.api.model import *
from react.api.terminals import *
from react.api.types import *


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
        self.data = CarData(name="car",pos_x=0,pos_y=0,v_x=0,v_y=0)
        self.trigger(Register(sender= self, data = self.data))

    def eevery_1s(self):
        self.data.pos_x = self.data.pos_x + self.data.v_x
        self.data.pos_y = self.data.pos_y + self.data.v_y
        self.trigger(UpdatePosition())

    ##TODO: unreg


class Master(Machine):
    cars = listof(Car)

    def on_start(self):
        self.cars = []
        #print self
        #print self.cars

    def every_1s(self):
        for car in self.cars:
            self.trigger(UpdateSensor(sender=self, receiver=car, cars = self.cars))



"""
  Events
"""
class Register(Event):
    sender   = { "car": Car }
    receiver = { "master": Master }
    data = CarData


    def guard(self):
        return None
        #if self.data.name in [car.data.name for car in Car.all()]: return "Name taken"

    def handler(self):
        #print "1"
        self.car.data = self.data
        #print "2"
        self.master.cars.append(self.car)
        return self.car

class UpdatePosition(Event):
    sender   = { "car": Car }
    receiver = { "master": Master }

    def guard(self):
        pass

    def handler(self):
        for car in self.master.cars:
            if car.id() == self.car.id():
                car = self.car
        return self.car

class UpdateSensor(Event):
    sender   = { "master": Master }
    receiver = { "car": Car }
    cars = listof(Car)


    def guard(self):
        pass

    #move computation to master
    def handler(self):
        print "received %d close cars" % len(self.cars)
        closeCars = []
        for otherCar in self.cars:
            if abs(self.car.data.pos_x - otherCar.data.pos_x) <= 5:
                if abs(self.car.data.pos_y - otherCar.data.pos_y) <= 5:
                    closeCars.append(otherCar.data)
        self.car.closeCars = closeCars
        return closeCars
