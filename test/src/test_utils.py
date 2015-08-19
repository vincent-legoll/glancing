#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import unittest
import StringIO

from tutils import get_local_path

# Setup PYTHONPATH for utils
sys.path.append(get_local_path('..', '..', 'src'))

import utils

class TestUtils(unittest.TestCase):

    def test_get_verbose_is_boolean(self):
        v = utils.get_verbose()
        self.assertTrue((v is True) or (v is False))

    def test_set_verbose_toggle(self):
        v = utils.get_verbose()
        utils.set_verbose()
        self.assertFalse(v == utils.get_verbose())
        utils.set_verbose()
        self.assertTrue(v == utils.get_verbose())

    def test_set_verbose_value(self):
        v = utils.get_verbose()
        utils.set_verbose(True)
        self.assertTrue(utils.get_verbose() is True)
        utils.set_verbose(False)
        self.assertTrue(utils.get_verbose() is False)
        utils.set_verbose(v)
        self.assertTrue(utils.get_verbose() == v)

    def test_vprint(self):
        v = utils.get_verbose()
        utils.set_verbose(True)
        with utils.stringio() as output:
            with utils.redirect('stdout', output):
                utils.vprint('TOTOTITI', utils.test_name())
                self.assertEqual(utils.test_name() + ': TOTOTITI\n', output.getvalue())
            self.assertEqual(utils.test_name() + ': TOTOTITI\n', output.getvalue())
        with self.assertRaises(ValueError):
            output.getvalue()
        utils.set_verbose(v)

    def utils_test_test_name(self):
        self.assertEqual(utils.test_name(), 'utils_test_test_name')

class TestUtilsRun(unittest.TestCase):

    def utils_test_run_true(self):
        self.assertTrue(utils.run(['true'])[0])

    def utils_test_run_no_exe(self):
        self.assertFalse(utils.run(['n o t h i n g'])[0])

    def utils_test_run_false(self):
        self.assertFalse(utils.run(['false'])[0])

    def utils_test_run_false(self):
        good, retcode, out, err = utils.run(['ls', '--format'], out=True, err=True)
        self.assertFalse(good)
        self.assertFalse(0 == retcode)
        self.assertEqual('', out)
        self.assertFalse('' == err)

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

class TestUtilsStringio(unittest.TestCase):

    def test_stringio_write(self):
        with utils.stringio() as out:
            out.write('TOTO')
            self.assertEqual('TOTO', out.getvalue())
        self.assertTrue(out.closed)

    def test_stringio_read(self):
        with utils.stringio() as out:
            self.assertEqual('', out.getvalue())
            self.assertEqual('', out.read())
            out.write('TOTO')
            self.assertEqual('TOTO', out.getvalue())
            self.assertEqual('', out.read())
            out.seek(0)
            self.assertEqual('TOTO', out.getvalue())
            self.assertEqual('TOTO', out.read())
            out.seek(0, os.SEEK_END)
            out.write('TITI')
            self.assertEqual('TOTOTITI', out.getvalue())
            self.assertEqual('', out.read())
            out.seek(0)
            self.assertEqual('TOTOTITI', out.read())
            out.seek(0)
            out.write('TITI')
            self.assertEqual('TITITITI', out.getvalue())
            self.assertEqual('TITI', out.read())
            out.seek(0)
            self.assertEqual('TITITITI', out.read())
        self.assertTrue(out.closed)

    def test_fileio_read(self):
        test_file = 'test.txt'
        utils.run(['touch', test_file])
        with utils.cleanup(['rm', test_file]):
            with open(test_file, 'rw+b') as out:
                self.assertEqual('', out.read())
                out.write('TOTO')
                self.assertEqual('', out.read())
                out.seek(0)
                self.assertEqual('TOTO', out.read())
                out.seek(0, os.SEEK_END)
                out.write('TITI')
                self.assertEqual('', out.read())
                out.seek(0)
                self.assertEqual('TOTOTITI', out.read())
                out.seek(0)
                out.write('TITI')
                self.assertEqual('TITI', out.read())
                out.seek(0)
                self.assertEqual('TITITITI', out.read())
            self.assertTrue(out.closed)

class TestUtilsRedirect(unittest.TestCase):

    def test_print(self):
        with utils.stringio() as output:
            with utils.redirect('stdout', output):
                print('TOTOTITI')
                self.assertEqual('TOTOTITI\n', output.getvalue())
            self.assertEqual('TOTOTITI\n', output.getvalue())
        with self.assertRaises(ValueError):
            output.getvalue()

    def test_close(self):
        tmp = None
        with utils.redirect('stdout'):
            print('toto')
            print('toto', file=sys.stdout)
            self.assertFalse(sys.stdout.closed)
            tmp = sys.stdout
        self.assertFalse(sys.stdout.closed)
        self.assertTrue(tmp.closed)

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

        print('samarche')
        with utils.devnull('stdout'):
            print('sareum')
            print('sonreup', file=sys.stderr)
        print('samarchedenouveau')

        self._commit()

        self.assertEqual(open('test_devnull_err.txt', 'rb').read(), 'sonreup\n')
        self.assertEqual(open('test_devnull_out.txt', 'rb').read(), 'samarche\nsamarchedenouveau\n')

    def utils_test_devnull_print_explicit(self):

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

zde = ZeroDivisionError('integer division or modulo by zero')
ae = ArithmeticError('integer division or modulo by zero')

class TestComparableExc(unittest.TestCase):

    def setUp(self):
        try:
            0 / 0
        except Exception as e:
            self.e = e

    def utils_test_cexc_simple_empties(self):

        # Empty iterables
        self.assertNotIn(self.e, [])
        self.assertNotIn(self.e, tuple())
        self.assertNotIn(self.e, set())
        self.assertNotIn(self.e, frozenset())
        self.assertNotIn(self.e, {})

        # containing itself
        self.assertIn(self.e, [self.e])
        self.assertIn(self.e, (self.e,))
        self.assertIn(self.e, set((self.e,)))
        self.assertIn(self.e, set([self.e]))
        self.assertIn(self.e, frozenset((self.e,)))
        self.assertIn(self.e, frozenset([self.e]))
        self.assertIn(self.e, {self.e: 1})
        self.assertNotIn(self.e, {1: self.e})

    def utils_test_cexc_compatible_excs(self):

        # Compatible Exceptions
        self.assertIn(self.e, utils.Exceptions(zde))
        self.assertNotIn(self.e, utils.Exceptions(ae))

        # Those two are equivalent
        self.assertIn(self.e, utils.Exceptions(zde, ae))
        self.assertIn(self.e, utils.Exceptions(
            ZeroDivisionError('integer division or modulo by zero'),
            ArithmeticError('integer division or modulo by zero'),
        ))

    def utils_test_cexc_sets(self):

        to_test_in = [(zde,), [zde], {zde}, (ae, zde), [ae, zde]]
        to_test_not_in = [(ae,), [ae], {ae}]

        for it in to_test_in:
            self.assertIn(self.e, utils.Exceptions(set(it)))
            self.assertIn(self.e, utils.Exceptions(frozenset(it)))

        for it in to_test_not_in:
            self.assertNotIn(self.e, utils.Exceptions(set(it)))
            self.assertNotIn(self.e, utils.Exceptions(frozenset(it)))

    def utils_test_cexc_hashes(self):

        to_test_in = [{zde: 1}, {ae: 1, zde: 2}, {zde: False, None: 0, True: 1, False: 0}]
        to_test_not_in = [{1: zde}, {1: zde, 1: ae}, {ae: False, None: 0, True: 1, False: 0}, {ae: 1}, {1: ae}]

        for it in to_test_in:
            self.assertIn(self.e, utils.Exceptions(it))

        for it in to_test_not_in:
            self.assertNotIn(self.e, utils.Exceptions(it))

class TestExceptions(unittest.TestCase):

    excs = (
                Exception,
                Exception(None),
                Exception(True),
                Exception(False),
                Exception(''),
                Exception('Yo'),
                NotImplementedError(),
                NotImplementedError(''),
                NotImplementedError('n i m b y'),
                ValueError('n i m b y'),
                ValueError('Yo'),

                # Containers: keep their content different, or they'll match each other
                Exception(dict()),
                Exception(tuple()),
                Exception(list()),
                Exception(set()),
                Exception(frozenset([None])),
                Exception({0: 2}),
                Exception(tuple([0])),
                Exception([0]),
                Exception(set([0])),
                Exception(frozenset([1])),
                Exception({2}),
    )

    def utils_test_loop(self):

        for exc in self.excs:
            try:
                if isinstance(exc, Exception):
                    # Should not raise e directly, make a copy
                    raise exc.__class__(*exc.args)
                elif type(exc) == type(Exception):
                    raise exc
                else:
                    self.assertTrue(False)
            except Exception as e:
                self.assertFalse(e is exc)
                self.assertIn(e, utils.Exceptions(self.excs))
                a = list(self.excs)
                a.remove(exc)
                self.assertNotIn(e, utils.Exceptions(a))
