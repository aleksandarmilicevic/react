#!/usr/bin/env python
# PKG = 'react'
#import roslib; roslib.load_manifest(PKG)

import sys
import unittest

from react.api.model import *
from react.helpers.test.model_test_helper import ModelTestHelper

class TestModel(unittest.TestCase, ModelTestHelper):
    def test_record(self):  self.assert_record_cls(Record, RecordMeta)
    def test_machine(self): self.assert_record_cls(Machine,  MachineMeta)
    def test_event(self):   self.assert_record_cls(Event, EventMeta)

if __name__ == '__main__':
    import rosunit
    rosunit.unitrun('react', 'test_model', TestModel)
