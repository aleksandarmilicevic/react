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
from react.helpers.listener_helper import ListenerHelper

class TestChat(unittest.TestCase, ModelTestHelper, ListenerHelper):
    def assert_sender_receiver(self, ev_cls):
        self.assertEqual("client", ev_cls.meta().sender_fld_name())
        self.assertEqual("server", ev_cls.meta().receiver_fld_name())

    def test_msg(self):
        self.check_all(Msg)
        self.assert_rec_cls(Msg, RecordMeta, sender="User", text="str")

        self.reg_lstner()
        self.assert_obj_field_vals(Msg, sender=None, text="")
        self.unreg_lstner()

        acc_num = len(self.accesses) 
        self.assertSetEqual(set(["sender", "text"]), set(self.read_fld_names()))

        m = Msg()
        self.assertEqual("", m.text)
        self.assertIsNone(m.sender)
        self.check_all(Msg)

        # test that unreg worked, ie no more accesses were added
        self.assertEqual(acc_num, len(self.accesses))

        self.reg_lstner()
        m.text = "hi there"
        self.unreg_lstner()

        self.assertEqual(["text"], self.write_fld_names())

    def test_user(self):
        self.check_all(User)
        self.assert_rec_cls(User, RecordMeta, "name")
        self.assert_obj_field_vals(User, name="")

    def test_room(self):
        self.check_all(ChatRoom)
        self.assert_rec_cls(ChatRoom, RecordMeta, "name", "members", "msgs")
        self.assert_obj_field_vals(ChatRoom, name="", members=list(), msgs=list())
        self.assertEqual(list(), ChatRoom().members)
        self.assertEqual(list(), ChatRoom().msgs)

    def test_client(self):
        self.check_all(Client)
        self.assert_rec_cls(Client, MachineMeta, "user", "rooms")
        self.assert_obj_field_vals(Client, user=None, rooms=list())

    def test_server(self):
        self.check_all(Server)
        self.assert_rec_cls(Server, MachineMeta, "clients", "rooms")
        self.assert_obj_field_vals(Server, clients=list(), rooms=list())

    def test_register(self):
        self.check_all(Register)
        self.assert_rec_cls(Register, EventMeta, "client", "server", "name")
        self.assert_sender_receiver(Register)

    def test_listrooms(self):
        self.check_all(ListRooms)
        self.assert_rec_cls(ListRooms, EventMeta, "client", "server")
        self.assert_sender_receiver(ListRooms)

    def test_createroom(self):
        self.check_all(CreateRoom)
        self.assert_rec_cls(CreateRoom, EventMeta, "client", "server", "name")
        self.assert_sender_receiver(CreateRoom)

if __name__ == '__main__':
    # import rosunit; rosunit.unitrun('react', 'test_chat', TestChat)
    unittest.main()

