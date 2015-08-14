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

ce_zde = utils.ComparableExc(ZeroDivisionError, ('integer division or modulo by zero',))
ce_ae = utils.ComparableExc(ArithmeticError, ('integer division or modulo by zero',))

class TestComparableExc(unittest.TestCase):

    def utils_test_cexc_simple(self):
        
        try:
            0 / 0
        except Exception as e:

            self.assertEqual(e, ce_zde)
            self.assertNotEqual(e, ce_ae)

            # Need both, as there's 2 methods to test __eq__() & __ne__()
            self.assertTrue(e == ce_zde)
            self.assertFalse(e != ce_zde)

            # Need both, as there's 2 methods to test __eq__() & __ne__()
            self.assertFalse(e == ce_ae)
            self.assertTrue(e != ce_ae)

            # Empty iterables
            self.assertNotIn(e, [])
            self.assertNotIn(e, tuple())
            self.assertNotIn(e, set())
            self.assertNotIn(e, {})

            # iterables containing it
            self.assertIn(e, [ce_zde])
            self.assertIn(e, (ce_zde,))

            # iterables not containing it
            self.assertNotIn(e, [ce_ae])
            self.assertNotIn(e, (ce_ae,))

            # iterables containing it and others
            self.assertIn(e, [ce_ae, ce_zde])
            self.assertIn(e, (ce_ae, ce_zde))

    @unittest.skip('unhashable')
    def utils_test_cexc_sets(self):
        
        try:
            0 / 0
        except Exception as e:

            # containing it
            self.assertIn(e, set((ce_zde,)))
            self.assertIn(e, set([ce_zde]))

            # not containing it
            self.assertNotIn(e, set((ce_ae,)))
            self.assertNotIn(e, set([ce_ae]))

            # containing it and others
            self.assertIn(e, set((ce_ae, ce_zde)))
            self.assertIn(e, set([ce_ae, ce_zde]))

    @unittest.skip('unhashable')
    def utils_test_cexc_frozensets(self):
        
        try:
            0 / 0
        except Exception as e:

            # containing it
            self.assertIn(e, frozenset((ce_zde,)))
            self.assertIn(e, frozenset([ce_zde]))

            # not containing it
            self.assertNotIn(e, frozenset((ce_ae,)))
            self.assertNotIn(e, frozenset([ce_ae]))

            # containing it and others
            self.assertIn(e, frozenset((ce_ae, ce_zde)))
            self.assertIn(e, frozenset([ce_ae, ce_zde]))

    @unittest.skip('unhashable')
    def utils_test_cexc_hashes(self):
        
        try:
            0 / 0
        except Exception as e:

            try:
                0 / 0
            except Exception as f:

                self.assertFalse(e is f)
                self.assertTrue(e == f)
                self.assertIn(e, {e: 1})
                self.assertIn(e, {1: e})

                self.assertIn(e, {ce_zde: 1})
                self.assertNotIn(e, {1: ce_zde})
                self.assertNotIn(e, {1: ce_ae})
                self.assertIn(e, {1: ce_ae, 2: ce_zde})

    def utils_test_cexc_cmp_excs(self):
        
        try:
            0 / 0
        except Exception as e:
            self.assertIn(e, utils.cmp_excs([
                (ZeroDivisionError, 'integer division or modulo by zero'),
                (ArithmeticError, 'integer division or modulo by zero'),]))

    def utils_test_cexc_cmp_excs_notin(self):
        
        try:
            raise NotImplementedError('n i m b y')
        except Exception as e:
            self.assertNotIn(e, utils.cmp_excs([
                (None, None),
                (None, ''),
                (Exception, None),
                (Exception, ''),
                (NotImplementedError, None),
                (NotImplementedError, ''),
                ]))

    def utils_test_cexc_cmp_excs_in(self):
        
        try:
            raise NotImplementedError('n i m b y')
        except Exception as e:
            self.assertIn(e, utils.cmp_excs([
                (None, None),
                (None, ''),
                (Exception, None),
                (Exception, ''),
                (NotImplementedError, None),
                (NotImplementedError, 'n i m b y'),
                ]))

    def utils_test_cexc_cmp_excs_generic0(self):
        
        try:
            raise Exception
        except Exception as e:
            self.assertNotIn(e, utils.cmp_excs([
                (None, None),
                (None, ''),
                (Exception, None),
                (Exception, ''),
                (NotImplementedError, None),
                (ValueError, 'n i m b y'),
                ]))

    def utils_test_cexc_cmp_excs_generic0bis(self):
        
        try:
            raise Exception
        except Exception as e:
            self.assertIn(e, utils.cmp_excs([
                (None, None),
                (None, ''),
                (Exception,),
                (Exception, ''),
                (NotImplementedError, None),
                (ValueError, 'n i m b y'),
                ]))

    def utils_test_cexc_cmp_excs_generic0bis_simple(self):
        
        try:
            raise Exception
        except Exception as e:
            ee = utils.ComparableExc(Exception, tuple())
            self.assertEqual(e, ee)

    def utils_test_cexc_cmp_excs_generic1(self):
        
        try:
            raise Exception()
        except Exception as e:
            self.assertNotIn(e, utils.cmp_excs([
                (None, None),
                (None, ''),
                (Exception, None),
                (Exception, ''),
                (NotImplementedError, None),
                (ValueError, 'n i m b y'),
                ]))

    def utils_test_cexc_cmp_excs_generic1bis(self):
        
        try:
            raise Exception()
        except Exception as e:
            self.assertIn(e, utils.cmp_excs([
                (None, None),
                (None, ''),
                (Exception,),
                (Exception, ''),
                (NotImplementedError, None),
                (ValueError, 'n i m b y'),
                ]))

    def utils_test_cexc_cmp_excs_generic1bis_simple(self):
        
        try:
            raise Exception()
        except Exception as e:
            ee = utils.ComparableExc(Exception, tuple())
            self.assertEqual(e, ee)

    def utils_test_cexc_cmp_excs_generic2(self):
        
        try:
            raise Exception('')
        except Exception as e:
            self.assertIn(e, utils.cmp_excs([
                (None, None),
                (None, ''),
                (Exception, None),
                (Exception, ''),
                (NotImplementedError, None),
                (ValueError, 'n i m b y'),
                ]))

    def utils_test_cexc_cmp_excs_generic3(self):
        
        try:
            raise Exception('Yo')
        except Exception as e:
            self.assertNotIn(e, utils.cmp_excs([
                (None, None),
                (None, ''),
                (Exception, None),
                (Exception, ''),
                (NotImplementedError, None),
                (ValueError, 'Yo'),
                ]))
