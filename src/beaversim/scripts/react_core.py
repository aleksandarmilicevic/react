#!/usr/bin/env python

import react
from react import conf
from react import core
from react.core import node

from beaversim.model import *

if __name__ == "__main__":
    conf.cli = conf.E_THR_OPT.FALSE
    react.core.node.ReactCore().start_core()
