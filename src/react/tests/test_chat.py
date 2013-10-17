#!/usr/bin/env python
# PKG = 'react'
#import roslib; roslib.load_manifest(PKG)

import sys
import unittest
import react

from react.examples.chat.chat_model import *
from react.api.model import * 
from react.api.metamodel import * 
from react.helpers.test.model_test_helper import ModelTestHelper

class TestChat(unittest.TestCase, ModelTestHelper):
    def assert_sender_receiver(self, ev_cls):
        self.assertEqual("client", ev_cls.meta().sender_fld_name())
        self.assertEqual("server", ev_cls.meta().receiver_fld_name())

    def test_msg(self):  self.assert_rec_cls(Msg, RecordMeta, sender="User", text="str")
    def test_user(self): self.assert_rec_cls(User, RecordMeta, "name")
    def test_room(self): self.assert_rec_cls(ChatRoom, RecordMeta, "name", "members", "msgs")
    def test_client(self): self.assert_rec_cls(Client, MachineMeta, "user", "rooms")
    def test_server(self): self.assert_rec_cls(Server, MachineMeta, "clients", "rooms")
    def test_register(self):
        self.assert_rec_cls(Register, EventMeta, "client", "server", "name")
        self.assert_sender_receiver(Register)
    def test_listrooms(self):
        self.assert_rec_cls(ListRooms, EventMeta, "client", "server")
        self.assert_sender_receiver(ListRooms)
    def test_createroom(self):
        self.assert_rec_cls(CreateRoom, EventMeta, "client", "server", "name")
        self.assert_sender_receiver(CreateRoom)

if __name__ == '__main__':
    import rosunit
    # unittest.main()
    rosunit.unitrun('react', 'test_chat', TestChat)
