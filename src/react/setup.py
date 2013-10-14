#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['react', 'react.api', 'react.helpers', 'react.helpers.test'],
    package_dir={'': 'src'},
    install_requires=[],
)

setup(**d)
