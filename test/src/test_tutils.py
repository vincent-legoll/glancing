#! /usr/bin/env python

import unittest

import tutils

class TestTutils(unittest.TestCase):

    def tutils_test_mod_path(self):
        self.assertTrue(tutils.mod_path().endswith('/glancing/test/src'))

    def tutils_test_get_local_path(self):
        lp = tutils.get_local_path('toto', 'titi.txt')
        self.assertTrue(lp.endswith('/glancing/test/src/toto/titi.txt'))
