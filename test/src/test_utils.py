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
        lp = utils.get_local_path('toto', 'titi.txt')
        self.assertTrue(lp.endswith('/glancing/test/src/toto/titi.txt'))

    def utils_test_devnull(self):
        if os.path.exists('test_devnull_out.txt'):
            os.remove('test_devnull_out.txt')
        if os.path.exists('test_devnull_err.txt'):
            os.remove('test_devnull_err.txt')
        with open('test_devnull_out.txt', 'wb') as out:
            with open('test_devnull_err.txt', 'wb') as err:
                old_out = sys.stdout
                old_err = sys.stderr
                sys.stdout = out
                sys.stderr = err

                print('samarche', file=sys.stdout)
                with utils.devnull('stdout'):
                    print('sareum', file=sys.stdout)
                    print('sonreup', file=sys.stderr)
                print('samarchedenouveau', file=sys.stdout)

                sys.stdout = old_out
                sys.stderr = old_err

        self.assertEqual(open('test_devnull_err.txt', 'rb').read(), 'sonreup\n')
        self.assertEqual(open('test_devnull_out.txt', 'rb').read(), 'samarche\nsamarchedenouveau\n')
        if os.path.exists('test_devnull_out.txt'):
            os.remove('test_devnull_out.txt')
        if os.path.exists('test_devnull_err.txt'):
            os.remove('test_devnull_err.txt')

    def utils_test_environ_not_existent_val(self):
        self.assertTrue('TOTO' not in os.environ)
        with utils.environ('TOTO', 'titi'):
            self.assertEqual('titi', os.environ['TOTO'])
        self.assertTrue('TOTO' not in os.environ)

    def utils_test_environ_not_existent_no_val(self):
        self.assertTrue('TOTO' not in os.environ)
        with utils.environ('TOTO'):
            self.assertEqual('', os.environ['TOTO'])
        self.assertTrue('TOTO' not in os.environ)

    def utils_test_environ_existent_val(self):
        self.assertTrue('TOTO' not in os.environ)
        os.environ['TOTO'] = 'tutu'
        self.assertEqual('tutu', os.environ['TOTO'])
        with utils.environ('TOTO', 'titi'):
            self.assertEqual('titi', os.environ['TOTO'])
        self.assertEqual('tutu', os.environ['TOTO'])
        del os.environ['TOTO']
        self.assertTrue('TOTO' not in os.environ)
