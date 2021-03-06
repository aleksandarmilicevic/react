from react.api.model import *
from react.api.types import *

"""
  Records
"""
class User(Record):
    name = str

class Msg(Record):
    sender = User
    text   = str

class ChatRoom(Record):
    name    = str
    members = listof(User)
    msgs    = listof(Msg)

"""
  Machines
"""
class Client(Machine):
    user  = User
    rooms = listof(ChatRoom)

class Server(Machine):
    rooms   = listof(ChatRoom)

    def onListRooms(self, event):
        print "listing rooms"

"""
  Events
"""
class Register(Event):
    sender   = { "client": Client }
    receiver = { "server": Server }
    name     = str

    def guard(self):
        if self.name in [user.name for user in User.all()]: return "Username taken"

    def handler(self):
        self.client.user = User(name = self.name)
        return self.client.user

class ListRooms(Event):
    sender   = { "client": Client }
    receiver = { "server": Server }

    def handler(self):
        return self.server.rooms

class CreateRoom(Event):
    sender   = { "client": Client }
    receiver = { "server": Server }
    name     = str

    def guard(self):
        if self.client.user is None: return "Not logged in"

    def handler(self):
        room = ChatRoom(name = self.name)
        room.members = [self.client.user]
        room.msgs = []
        self.server.rooms.append(room)
        return room

class JoinRoom(Event):
    sender   = { "client": Client }
    receiver = { "server": Server }
    params   = { "room":   ChatRoom }

    def guard(self):
        if self.client.user is None:           return "Not logged in"
        if not self.room in self.server.rooms: return "Room not found"
        if self.client.user in self.room:      return "User already member"

    def handler(self):
        self.client.my_rooms.append(self.room)
        self.room.members.append(self.client.user)

class SendMsg(Event):
    sender   = { "client": Client }
    receiver = { "server": Server }
    params   = { "msg":    str,
                 "room":   ChatRoom }

    def guard(self):
        if self.client is None:               return "Not logged in"
        if not self.client.user in self.room: return "User not a room member"

    def handler(self):
        msg = Msg(sender = self.client.uesr,
                  text   = self.msg)
        room.msgs.append(msg)
