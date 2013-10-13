#!/usr/bin/env python
# PKG = 'react'
#import roslib; roslib.load_manifest(PKG)

import sys
import unittest

from react.api.model import *

class TestModel(unittest.TestCase):
    def test_record(self):
        self.assertTrue(Record)
        self.assertEqual(RecordMeta, Record.__metaclass__)

if __name__ == '__main__':
    import rosunit
    rosunit.unitrun('react', 'test_model', TestModel)
