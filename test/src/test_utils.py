#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import unittest

import utils

class TestUtils(unittest.TestCase):

    def utils_test_mod_path(self):
        self.assertTrue(utils.mod_path().endswith('/glancing/test/src'))

    def utils_test_get_local_path(self):
        self.assertTrue(utils.get_local_path('toto', 'titi.txt').endswith(
        '/glancing/test/src/toto/titi.txt'))

    def utils_test_devnull(self):
        if os.path.exists('test_devnull_out.txt'):
            os.remove('test_devnull_out.txt')
        if os.path.exists('test_devnull_err.txt'):
            os.remove('test_devnull_err.txt')
        with open('test_devnull_out.txt', 'wb') as out:
            with open('test_devnull_err.txt', 'wb') as err:
                sys.stdout = out
                sys.stderr = err

                print('samarche', file=sys.stdout)
                with utils.devnull('stdout'):
                    print('sareum', file=sys.stdout)
                    print('sonreup', file=sys.stderr)
                print('samarchedenouveau', file=sys.stdout)
        self.assertEqual(open('test_devnull_err.txt', 'rb').read(), 'sonreup\n')
        self.assertEqual(open('test_devnull_out.txt', 'rb').read(), 'samarche\nsamarchedenouveau\n')
        if os.path.exists('test_devnull_out.txt'):
            os.remove('test_devnull_out.txt')
        if os.path.exists('test_devnull_err.txt'):
            os.remove('test_devnull_err.txt')
