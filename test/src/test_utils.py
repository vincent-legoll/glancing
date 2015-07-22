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

    def utils_test_test_name(self):
        self.assertEqual(utils.test_name(), 'utils_test_test_name')

    def utils_test_run_true(self):
        self.assertTrue(utils.run(['true'])[0])

    def utils_test_run_no_exe(self):
        self.assertFalse(utils.run(['n o t h i n g'])[0])

    def utils_test_run_false(self):
        utils.set_verbose(True)
        self.assertFalse(utils.run(['false'])[0])
        utils.set_verbose(False)

    def utils_test_run_not_in_path(self):
        with utils.environ('PATH'):
            self.assertFalse(utils.run(['true'])[0])

    def utils_test_run_file(self):
        test_file = '/tmp/' + utils.test_name()
        if os.path.exists(test_file):
            os.remove(test_file)
        self.assertTrue(utils.run(['touch', test_file])[0])
        self.assertTrue(os.path.exists(test_file))
        self.assertTrue(utils.run(['rm', test_file])[0])
        self.assertFalse(os.path.exists(test_file))

    def utils_test_run_output(self):
        good, retcode, out, err = utils.run(['echo', '-n', 'TOTO'], out=True)
        self.assertTrue(good)
        self.assertTrue(retcode == 0)
        self.assertEqual(out, 'TOTO')
        self.assertIsNone(err)

class TestUtilsDevnull(unittest.TestCase):

    def _cleanup_files(self):
        if os.path.exists('test_devnull_out.txt'):
            os.remove('test_devnull_out.txt')
        if os.path.exists('test_devnull_err.txt'):
            os.remove('test_devnull_err.txt')

    def _commit(self):
        self.out.flush()
        self.err.flush()
        os.fsync(self.out.fileno())
        os.fsync(self.err.fileno())

    def setUp(self):
        self._cleanup_files()
        self.out = open('test_devnull_out.txt', 'wb')
        self.err = open('test_devnull_err.txt', 'wb')
        self.old_out = sys.stdout
        self.old_err = sys.stderr
        sys.stdout = self.out
        sys.stderr = self.err

    def tearDown(self):
        sys.stdout = self.old_out
        sys.stderr = self.old_err
        self.out.close()
        self.err.close()
        self._cleanup_files()

    def utils_test_devnull_print(self):

        print('samarche', file=sys.stdout)
        with utils.devnull('stdout'):
            print('sareum', file=sys.stdout)
            print('sonreup', file=sys.stderr)
        print('samarchedenouveau', file=sys.stdout)

        self._commit()

        self.assertEqual(open('test_devnull_err.txt', 'rb').read(), 'sonreup\n')
        self.assertEqual(open('test_devnull_out.txt', 'rb').read(), 'samarche\nsamarchedenouveau\n')

    def utils_test_devnull_write(self):

        sys.stdout.write('samarche')
        with utils.devnull('stdout'):
            sys.stdout.write('sareum')
            sys.stderr.write('sonreup')
        sys.stdout.write('samarchedenouveau')

        self._commit()

        self.assertEqual(open('test_devnull_err.txt', 'rb').read(), 'sonreup')
        self.assertEqual(open('test_devnull_out.txt', 'rb').read(), 'samarchesamarchedenouveau')

class TestUtilsEnviron(unittest.TestCase):

    def setUp(self):
        self._old_toto_was_here = False
        if 'TOTO' in os.environ:
            self._old_toto_was_here = True
            self._old_toto_val = os.environ['TOTO']
            del os.environ['TOTO']

    def tearDown(self):
        if self._old_toto_was_here:
            os.environ['TOTO'] = self._old_toto_val

    def utils_test_environ_not_existent_val(self):
        self.assertTrue('TOTO' not in os.environ) # Paranoid
        with utils.environ('TOTO', 'titi'):
            self.assertEqual('titi', os.environ['TOTO'])
        self.assertTrue('TOTO' not in os.environ)

    def utils_test_environ_not_existent_no_val(self):
        self.assertTrue('TOTO' not in os.environ) # Paranoid
        with utils.environ('TOTO'):
            self.assertEqual('', os.environ['TOTO'])
        self.assertTrue('TOTO' not in os.environ)

    def utils_test_environ_existent_val(self):
        self.assertTrue('TOTO' not in os.environ) # Paranoid
        os.environ['TOTO'] = 'tutu'
        self.assertEqual('tutu', os.environ['TOTO'])
        with utils.environ('TOTO', 'titi'):
            self.assertEqual('titi', os.environ['TOTO'])
        self.assertEqual('tutu', os.environ['TOTO'])

    def utils_test_environ_existent_no_val(self):
        self.assertTrue('TOTO' not in os.environ) # Paranoid
        os.environ['TOTO'] = 'tutu'
        self.assertEqual('tutu', os.environ['TOTO'])
        with utils.environ('TOTO'):
            self.assertEqual('', os.environ['TOTO'])
        self.assertEqual('tutu', os.environ['TOTO'])

class TestUtilsCleanup(unittest.TestCase):

    def utils_test_cleanup(self):
        test_file = '/tmp/' + utils.test_name()
        self.assertFalse(os.path.exists(test_file))
        with utils.cleanup(['rm', test_file]):
            utils.run(['touch', test_file])
            self.assertTrue(os.path.exists(test_file))
        self.assertFalse(os.path.exists(test_file))
