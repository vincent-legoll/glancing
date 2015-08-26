#! /usr/bin/env python

import unittest

import tutils

class TutilsTest(unittest.TestCase):

    def test_tutils_mod_path(self):
        self.assertTrue(tutils.mod_path().endswith('/glancing/test/src'))

    def test_tutils_get_local_path(self):
        lp = tutils.get_local_path('toto', 'titi.txt')
        self.assertTrue(lp.endswith('/glancing/test/src/toto/titi.txt'))
