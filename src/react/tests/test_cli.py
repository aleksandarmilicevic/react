import react
import unittest

import react.core.cli as cli

from react.api.model import *
from react.helpers.test.model_test_helper import ModelTestHelper

class TestModel(unittest.TestCase):
    def test_parse1(self):
        cmd, name, params = cli.parse("trigger Register()")
        self.assertEqual("trigger", cmd)
        self.assertEqual("Register", name)
        self.assertEqual({}, params)

    def test_parse2(self):
        cmd, name, params = cli.parse("trigger Register")
        self.assertEqual("trigger", cmd)
        self.assertEqual("Register", name)
        self.assertEqual({}, params)

    def test_parse3(self):
        cmd, name, params = cli.parse("trigger Register(name='aleks')")
        self.assertEqual("trigger", cmd)
        self.assertEqual("Register", name)
        self.assertEqual({'name': 'aleks'}, params)

    def test_parse4(self):
        cmd, name, params = cli.parse("trigger Register(name='aleks', x = 1)")
        self.assertEqual("trigger", cmd)
        self.assertEqual("Register", name)
        self.assertEqual({'name': 'aleks', 'x': 1}, params)

if __name__ == '__main__':
    # import rosunit; rosunit.unitrun('react', 'test_model', TestModel)
    unittest.main()
