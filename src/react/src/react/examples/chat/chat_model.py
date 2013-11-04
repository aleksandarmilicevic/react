from react.api.model import *
from react.api.types import *

"""
  Records
"""
class User(Record):
    name = str
    def getAttr(self):
        return {"type":"User","name":self.name}

class Msg(Record):
    sender = User
    text   = str
    def getAttr(self):
        return {"type":"Msg","sender":self.sender.getAttr(),"msg":self.text}

class ChatRoom(Record):
    name    = str
    members = setof(User)
    msgs    = listof(Msg)
    def getAttr(self):
        memberList = []
        msgList = []
        for user in self.members:
            memberList.append(user.getAttr())
        for msg in self.msgs:
            msgList.append(msg.getAttr())
        return {"type":"ChatRoom","members":memberList,"msgs":msgList}

"""
  Machines
"""
class Client(Machine):
    user = User
    rooms = listof(ChatRoom)
    def getAttr(self):
        roomList = []
        for room in self.rooms:
            roomList.append(room.getAttr())
        if self.user != None:
            userAttr = self.user.getAttr()
        else:
            userAttr = {}
        return {"type":"Client","user":userAttr,"rooms":roomList}

class Server(Machine):
    clients = listof(Client)
    rooms   = listof(ChatRoom)
    def getAttr(self):
        clientList = []
        roomList = []
        for client in self.clients:
            clientList.append(client.getAttr())
        for room in self.rooms:
            roomList.append(room.getAttr())
        return {"type":"Server","Clients":clientList,"rooms":roomList}

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
        room.members = set(self.sender.user)
        room.msgs = []
        self.server.rooms.append(room)
        return room
    
class JoinRoom(Event):
    sender   = dict(client = Client)
    receiver = dict(server = Server)
    params   = dict(room   = ChatRoom)

    def guard(self):
        if self.client.user is None:           return "Not logged in"
        if not self.room in self.server.rooms: return "Room not found"
        if self.client.user in self.room:      return "User already member"

    def handler(self):
        self.client.my_rooms.append(self.room)
        self.room.members.append(self.client.user)

class SendMsg(Event):
    sender   = dict(client = Client)
    receiver = dict(server = Server)
    params   = dict(msg    = str,
                    room   = ChatRoom)
    
    def guard(self):
        if self.client is None:               return "Not logged in"
        if not self.client.user in self.room: return "User not a room member"

    def handler(self):
        msg = Msg(sender = self.client.uesr, 
                  text   = self.msg)
        room.msgs.append(msg)
