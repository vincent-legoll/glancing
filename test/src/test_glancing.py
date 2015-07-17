#! /usr/bin/env python

import sys
import unittest

from utils import get_local_path

# Setup PYTHONPATH for glancing
sys.path.append(get_local_path('..', '..', 'src'))

import glancing

class TestGlancing(unittest.TestCase):

    def glancing_test(self):
        pass

# args.digests : wrong size
