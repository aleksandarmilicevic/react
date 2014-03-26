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
class Master(Machine):
    cars = dict

    def every_1s(self):
        for carName in self.cars:
            self.trigger(UpdateSensor({"sender": self, "receiver": self.cars[carName]}))

            
class Car(Machine):
    data = CarData
    closeCars = listof(CarData)

    def on_start(self):
        self.trigger(Register,{"sender": self, "receiver": Master, "name": data.name,
                               "pos_x": data.pos_x, "pos_y": data.pos_y, "v_x": data.v_x, "v_y": data.v_y})
    
    def every_1s(self):
        self.data.pos_x = self.data.pos_x + self.data.v_x
        self.data.pos_y = self.data.pos_y + self.data.v_y
        self.trigger(UpdatePosition())

    ##TODO: unreg
    


"""
  Events
"""
class Register(Event):
    sender   = { "car": Car }
    receiver = { "master": Master }
    name     = str
    pos_x  = int
    pos_y  = int
    v_x    = int
    v_y    = int

    def guard(self):
        if self.name in [car.name for car in Car.all()]: return "Name taken"

    def handler(self):
        self.car.data = CarData(name = self.name, pos_x = self.pos_x, pos_y = self.pos_y, v_x = self.v_x, v_y = self.pos_y)
        self.master.cars[self.car.data.name] = self.car
        return self.car

class UpdatePosition(Event):
    sender   = { "car": Car }
    receiver = { "master": Master }

    def guard(self):
        pass

    def handler(self):
        self.master.cars[self.car.data.name] = self.car
        return self.car

class UpdateSensor(Event):
    sender   = { "master": Master }
    receiver = { "car": Car }

    def guard(self):
        pass

    def handler(self):
        closeCars = []
        for carName in self.master.cars:
            if abs(self.car.data.pos_x - self.master.cars[carName].data.pos_x) <= 5:
                if abs(self.car.data.pos_y - self.master.cars[carName].data.pos_y) <= 5:
                    closeCars.append(self.master.cars[carName].data)
        self.car.closeCars = closeCars
        return closeCars
