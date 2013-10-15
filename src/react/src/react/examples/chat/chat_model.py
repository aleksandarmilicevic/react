from react.api.model import *
from react.api.types import *

User     = record("User",     name    = str, 
                              friends = setof(str))
Msg      = record("Msg",      sender  = User, 
                              text    = str)
ChatRoom = record("ChatRoom", name    = str, 
                              members = setof(User),
                              msgs    = listof(Msg))

Client = machine("Client", user       = User, 
                           my_rooms   = listof(ChatRoom))
Server = machine("Server", clients    = listof(Client),
                           rooms      = listof(ChatRoom))

class Register(Event):
    sender   = dict(client = Client)
    receiver = dict(server = Server)
    params   = dict(name   = str)

    def guard(self):
        if self.name in [user.name for user in User.all]: return "Username taken"

    def handler(self):
        self.client.user = User(name = self.name)

class ListRooms(Event): 
    sender   = dict(client = Client)
    receiver = dict(server = Server)
    params   = dict()

    def handler(self):
        return self.server.rooms

class CreateRoom(Event):
    sender   = dict(client = Client)
    receiver = dict(server = Server)
    params   = dict(name   = str)

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
