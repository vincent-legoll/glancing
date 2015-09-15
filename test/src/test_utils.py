#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import uuid
import unittest

try:
    import StringIO
except ImportError:
    import io as StringIO

from tutils import local_pythonpath

# Setup project-local PYTHONPATH
local_pythonpath('..', '..', 'src')

import utils
from utils import size_t

class UtilsTestTempdir(unittest.TestCase):

    def test_utils_tempdir(self):
        oldcwd = os.getcwd()
        with utils.tempdir():
            tmp_cwd = os.getcwd()
            self.assertEqual('/tmp', os.path.dirname(tmp_cwd))
        self.assertEqual(os.getcwd(), oldcwd)
        self.assertFalse(os.path.exists(tmp_cwd))

class UtilsTestChdir(unittest.TestCase):

    def test_utils_chdir(self):
        oldcwd = os.getcwd()
        with utils.chdir('/tmp'):
            self.assertEqual(os.getcwd(), '/tmp')
        self.assertEqual(os.getcwd(), oldcwd)
        with self.assertRaises(ValueError):
            with utils.chdir(os.devnull):
                pass

class UtilsTestSizeT(unittest.TestCase):

    def test_utils_size_t_repr(self):
        self.assertEqual(repr(size_t(0)), '<size_t 0>')
        self.assertEqual(repr(size_t(0, 'B')), '<size_t 0B>')

        self.assertEqual(repr(size_t(2048)), '<size_t 2048>')
        self.assertEqual(repr(size_t(2048, 'B')), '<size_t 2048B>')

    def test_utils_size_t_str(self):
        self.assertEqual(str(size_t(0)), '0')
        self.assertEqual(str(size_t(0, 'B')), '0B')

        self.assertEqual(str(size_t(10)), '10')
        self.assertEqual(str(size_t(10, 'B')), '10B')

        self.assertEqual(str(size_t(666)), '666')
        self.assertEqual(str(size_t(667, 'B')), '667B')

        self.assertEqual(str(size_t(1023)), '1023')
        self.assertEqual(str(size_t(1024)), '1K')
        self.assertEqual(str(size_t(1025)), '1K')

        self.assertEqual(str(size_t(2047)), '1K')
        self.assertEqual(str(size_t(2048)), '2K')
        self.assertEqual(str(size_t(2049)), '2K')

        self.assertEqual(str(size_t(1024*1024-1)), '1023K')
        self.assertEqual(str(size_t(1024*1024+0)), '1M')
        self.assertEqual(str(size_t(1024*1024+1)), '1M')

        self.assertEqual(str(size_t(1024*1024*1024-1)), '1023M')
        self.assertEqual(str(size_t(1024*1024*1024+0)), '1G')
        self.assertEqual(str(size_t(1024*1024*1024+1)), '1G')

        self.assertEqual(str(size_t(1024*1024*1024*1024-1)), '1023G')
        self.assertEqual(str(size_t(1024*1024*1024*1024+0)), '1T')
        self.assertEqual(str(size_t(1024*1024*1024*1024+1)), '1T')

        self.assertEqual(str(size_t(1024*1024*1024*1024*1024+0)), '1P')
        self.assertEqual(str(size_t(1024*1024*1024*1024*1024+1)), '1P')

        # FIXME: This last one fail: 0P != 1023T
        #self.assertEqual(str(size_t(1024*1024*1024*1024*1024-1)), '1023T')

class UtilsTest(unittest.TestCase):

    def test_utils_get_verbose_is_boolean(self):
        v = utils.get_verbose()
        self.assertTrue((v is True) or (v is False))

    def test_utils_set_verbose_toggle(self):
        v = utils.get_verbose()
        utils.set_verbose()
        self.assertFalse(v == utils.get_verbose())
        utils.set_verbose()
        self.assertTrue(v == utils.get_verbose())

    def test_utils_set_verbose_value(self):
        v = utils.get_verbose()
        utils.set_verbose(True)
        self.assertTrue(utils.get_verbose() is True)
        utils.set_verbose(False)
        self.assertTrue(utils.get_verbose() is False)
        utils.set_verbose(v)
        self.assertTrue(utils.get_verbose() == v)

    def vprint_verbose(self, verbosity, test_name):
        v = utils.get_verbose()
        utils.set_verbose(verbosity)
        with utils.stringio() as output:
            expected = ''
            if verbosity:
                expected = test_name + ': TOTOTITI\n'
            with utils.redirect('stdout', output):
                utils.vprint('TOTOTITI', test_name)
                self.assertEqual(expected, output.getvalue())
            self.assertEqual(expected, output.getvalue())
        with self.assertRaises(ValueError):
            output.getvalue()
        utils.set_verbose(v)

    def vprint_lines_verbose(self, verbosity, test_name):
        v = utils.get_verbose()
        utils.set_verbose(verbosity)
        with utils.stringio() as output:
            expected = ''
            if verbosity:
                expected = test_name + ': TOTO\n' + test_name + ': TITI\n'
            with utils.redirect('stdout', output):
                utils.vprint_lines('TOTO\nTITI', test_name)
                self.assertEqual(expected, output.getvalue())
            self.assertEqual(expected, output.getvalue())
        with self.assertRaises(ValueError):
            output.getvalue()
        utils.set_verbose(v)

    def test_utils_vprint_verbose(self):
        self.vprint_verbose(True, utils.test_name())

    def test_utils_vprint_silent(self):
        self.vprint_verbose(False, utils.test_name())

    def test_utils_vprint_lines_verbose(self):
        self.vprint_lines_verbose(True, utils.test_name())

    def test_utils_vprint_lines_silent(self):
        self.vprint_lines_verbose(False, utils.test_name())

    def test_utils_test_name(self):
        self.assertEqual(utils.test_name(), 'test_utils_test_name')

    @unittest.skipIf(sys.version_info >= (3,), 'does not work on py3')
    def test_utils_block_read_filename(self):

        status = [False]

        def set_status(x):
            status[0] = True
       
        local_path = get_local_path('..', 'data', 'length_one.bin')

        utils.block_read_filename(local_path, set_status)
        self.assertTrue(status[0])

#    @unittest.skip('TODO')
#    def test_utils_block_read_filedesc(self):
#        pass

class UtilsRunTest(unittest.TestCase):

    def test_utils_run_true(self):
        self.assertTrue(utils.run(['true'])[0])

    def test_utils_run_no_exe(self):
        self.assertFalse(utils.run(['n o t h i n g'])[0])

    def test_utils_run_false(self):
        self.assertFalse(utils.run(['false'])[0])

    def test_utils_run_wrong(self):
        good, retcode, out, err = utils.run(['ls', '--format'], out=True, err=True)
        self.assertFalse(good)
        self.assertFalse(0 == retcode)
        self.assertEqual('', out)
        self.assertEqual(err, "ls: option '--format' requires an argument\nTry 'ls --help' for more information.\n")

    def test_utils_run_wrong_not_quiet(self):
        good, retcode, out, err = utils.run(['ls', '--format'], out=True, err=True, quiet_out=False, quiet_err=False)
        self.assertFalse(good)
        self.assertFalse(0 == retcode)
        self.assertEqual(out, '')
        self.assertEqual(err, "ls: option '--format' requires an argument\nTry 'ls --help' for more information.\n")

    def test_utils_run_not_in_path(self):
        with utils.environ('PATH'):
            self.assertFalse(utils.run(['true'])[0])

    def test_utils_run_file(self):
        test_file = '/tmp/' + utils.test_name()
        if os.path.exists(test_file):
            os.remove(test_file)
        self.assertTrue(utils.run(['touch', test_file])[0])
        self.assertTrue(os.path.exists(test_file))
        self.assertTrue(utils.run(['rm', test_file])[0])
        self.assertFalse(os.path.exists(test_file))

    def test_utils_run_output_quiet_false(self):
        good, retcode, out, err = utils.run(['echo', '-n', 'TOTO'], out=True, quiet_out=False)
        self.assertTrue(good)
        self.assertTrue(retcode == 0)
        self.assertEqual(out, 'TOTO')
        self.assertIsNone(err)

    def test_utils_run_output_quiet_true(self):
        good, retcode, out, err = utils.run(['echo', '-n', 'TOTO'], out=True, quiet_out=True)
        self.assertTrue(good)
        self.assertTrue(retcode == 0)
        self.assertEqual(out, 'TOTO')
        self.assertIsNone(err)

    def test_utils_run_output(self):
        good, retcode, out, err = utils.run(['echo', '-n', 'TOTO'], out=True)
        self.assertTrue(good)
        self.assertTrue(retcode == 0)
        self.assertEqual(out, 'TOTO')
        self.assertIsNone(err)

class UtilsUUIDTest(unittest.TestCase):

    def test_utils_is_uuid(self):
        self.assertTrue(utils.is_uuid(uuid.uuid4()))
        self.assertTrue(utils.is_uuid(str(uuid.uuid4())))
        self.assertFalse(utils.is_uuid(None))
        self.assertFalse(utils.is_uuid(True))
        self.assertFalse(utils.is_uuid(False))
        self.assertFalse(utils.is_uuid(''))
        self.assertFalse(utils.is_uuid(u''))
        self.assertFalse(utils.is_uuid([]))
        self.assertFalse(utils.is_uuid({}))
        self.assertFalse(utils.is_uuid(set()))
        self.assertFalse(utils.is_uuid(frozenset()))

class UtilsStringioTest(unittest.TestCase):

    def test_utils_stringio_write(self):
        with utils.stringio() as out:
            out.write('TOTO')
            self.assertEqual('TOTO', out.getvalue())
        self.assertTrue(out.closed)

    def test_utils_stringio_read(self):
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

    def test_utils_fileio_read(self):
        test_file = 'test.txt'
        utils.run(['touch', test_file])
        with utils.cleanup(['rm', test_file]):
            with open(test_file, 'w+b') as out:
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

class UtilsRedirectTest(unittest.TestCase):

    def test_utils_redirect_run(self):
        with utils.stringio() as output:
            with utils.redirect('stdout', output):
                utils.run(['echo', 'TOTO'], out=False)
                self.assertEqual('', output.getvalue())

    def test_utils_redirect_run_out(self):
        with utils.stringio() as output:
            with utils.redirect('stdout', output):
                utils.run(['echo', 'TOTO'], out=True)
                self.assertEqual('', output.getvalue())

    def test_utils_redirect_write(self):
        with utils.stringio() as output:
            with utils.redirect('stdout', output):
                sys.stdout.write('TOTO')
                self.assertEqual('TOTO', output.getvalue())

    def test_utils_redirect_print(self):
        with utils.stringio() as output:
            with utils.redirect('stdout', output):
                print('TOTOTITI')
                self.assertEqual('TOTOTITI\n', output.getvalue())
            self.assertEqual('TOTOTITI\n', output.getvalue())
        with self.assertRaises(ValueError):
            output.getvalue()

    def test_utils_redirect_close(self):
        tmp = None
        with utils.redirect('stdout'):
            print('toto')
            print('toto', file=sys.stdout)
            self.assertFalse(sys.stdout.closed)
            tmp = sys.stdout
        self.assertFalse(sys.stdout.closed)
        self.assertTrue(tmp.closed)

class UtilsDevnullTest(unittest.TestCase):

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

    def test_utils_devnull_print(self):

        print('samarche')
        with utils.devnull('stdout'):
            print('sareum')
            print('sonreup', file=sys.stderr)
        print('samarchedenouveau')

        self._commit()

        self.assertEqual(open('test_devnull_err.txt', 'rb').read(), 'sonreup\n')
        self.assertEqual(open('test_devnull_out.txt', 'rb').read(), 'samarche\nsamarchedenouveau\n')

    def test_utils_devnull_print_explicit(self):

        print('samarche', file=sys.stdout)
        with utils.devnull('stdout'):
            print('sareum', file=sys.stdout)
            print('sonreup', file=sys.stderr)
        print('samarchedenouveau', file=sys.stdout)

        self._commit()

        self.assertEqual(open('test_devnull_err.txt', 'rb').read(), 'sonreup\n')
        self.assertEqual(open('test_devnull_out.txt', 'rb').read(), 'samarche\nsamarchedenouveau\n')

    def test_utils_devnull_write(self):

        sys.stdout.write('samarche')
        with utils.devnull('stdout'):
            sys.stdout.write('sareum')
            sys.stderr.write('sonreup')
        sys.stdout.write('samarchedenouveau')

        self._commit()

        self.assertEqual(open('test_devnull_err.txt', 'rb').read(), 'sonreup')
        self.assertEqual(open('test_devnull_out.txt', 'rb').read(), 'samarchesamarchedenouveau')

class UtilsEnvironTest(unittest.TestCase):

    def setUp(self):
        self._old_toto_was_here = False
        if 'TOTO' in os.environ:
            self._old_toto_was_here = True
            self._old_toto_val = os.environ['TOTO']
            del os.environ['TOTO']

    def tearDown(self):
        if self._old_toto_was_here:
            os.environ['TOTO'] = self._old_toto_val

    def test_utils_environ_not_existent_val(self):
        self.assertTrue('TOTO' not in os.environ) # Paranoid
        with utils.environ('TOTO', 'titi'):
            self.assertEqual('titi', os.environ['TOTO'])
        self.assertTrue('TOTO' not in os.environ)

    def test_utils_environ_not_existent_no_val(self):
        self.assertTrue('TOTO' not in os.environ) # Paranoid
        with utils.environ('TOTO'):
            self.assertEqual('', os.environ['TOTO'])
        self.assertTrue('TOTO' not in os.environ)

    def test_utils_environ_existent_val(self):
        self.assertTrue('TOTO' not in os.environ) # Paranoid
        os.environ['TOTO'] = 'tutu'
        self.assertEqual('tutu', os.environ['TOTO'])
        with utils.environ('TOTO', 'titi'):
            self.assertEqual('titi', os.environ['TOTO'])
        self.assertEqual('tutu', os.environ['TOTO'])

    def test_utils_environ_existent_no_val(self):
        self.assertTrue('TOTO' not in os.environ) # Paranoid
        os.environ['TOTO'] = 'tutu'
        self.assertEqual('tutu', os.environ['TOTO'])
        with utils.environ('TOTO'):
            self.assertEqual('', os.environ['TOTO'])
        self.assertEqual('tutu', os.environ['TOTO'])

class UtilsCleanupTest(unittest.TestCase):

    def test_utils_cleanup(self):
        test_file = '/tmp/' + utils.test_name()
        self.assertFalse(os.path.exists(test_file))
        with utils.cleanup(['rm', test_file]):
            utils.run(['touch', test_file])
            self.assertTrue(os.path.exists(test_file))
        self.assertFalse(os.path.exists(test_file))

# Incompatibility with pypy (at least the 2.2.1 version)
zde_msg = 'integer division or modulo by zero'
if 'pypy_version_info' in dir(sys):
    zde_msg = 'integer division by zero'
zde = ZeroDivisionError(zde_msg)
ae = ArithmeticError(zde_msg)

class ComparableExcTest(unittest.TestCase):

    def setUp(self):
        try:
            0 / 0
        except Exception as e:
            self.e = e

    def test_utils_cexc_simple_empties(self):

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

    def test_utils_cexc_compatible_excs(self):

        # Compatible Exceptions
        self.assertIn(self.e, utils.Exceptions(zde))
        self.assertNotIn(self.e, utils.Exceptions(ae))

        # Those two are equivalent
        self.assertIn(self.e, utils.Exceptions(zde, ae))
        self.assertIn(self.e, utils.Exceptions(
            ZeroDivisionError(zde_msg),
            ArithmeticError(zde_msg),
        ))

    def test_utils_cexc_sets(self):

        to_test_in = [(zde,), [zde], {zde}, (ae, zde), [ae, zde]]
        to_test_not_in = [(ae,), [ae], {ae}]

        for it in to_test_in:
            self.assertIn(self.e, utils.Exceptions(set(it)))
            self.assertIn(self.e, utils.Exceptions(frozenset(it)))

        for it in to_test_not_in:
            self.assertNotIn(self.e, utils.Exceptions(set(it)))
            self.assertNotIn(self.e, utils.Exceptions(frozenset(it)))

    def test_utils_cexc_hashes(self):

        to_test_in = [{zde: 1}, {ae: 1, zde: 2}, {zde: False, None: 0, True: 1, False: 0}]
        to_test_not_in = [{1: zde}, {1: zde, 1: ae}, {ae: False, None: 0, True: 1, False: 0}, {ae: 1}, {1: ae}]

        for it in to_test_in:
            self.assertIn(self.e, utils.Exceptions(it))

        for it in to_test_not_in:
            self.assertNotIn(self.e, utils.Exceptions(it))

class ExceptionsTest(unittest.TestCase):

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
        None,
    )

    def test_utils_loop(self):

        for exc in self.excs:
            try:
                if isinstance(exc, Exception):
                    # Should not raise e directly, make a copy
                    raise exc.__class__(*exc.args)
                elif type(exc) == type(Exception):
                    raise exc
                else:
                    self.assertTrue(exc is None)
            except Exception as e:
                self.assertFalse(e is exc)
                self.assertIn(e, utils.Exceptions(self.excs))
                a = list(self.excs)
                a.remove(exc)
                self.assertNotIn(e, utils.Exceptions(a))

class AlmostRawFormatterTest(unittest.TestCase):

    def test_split_lines(self):
        rf = utils.AlmostRawFormatter('prog_name')
        with self.assertRaises(ValueError):
            rf._split_lines('', 0)
        test_vals = (
            ('', [], []),
            ('toto', ['toto'], ['toto']),
            ('toto\ntiti', ['toto', 'titi'], ['toto', 'titi']),
            ('toto\ntiti\n', ['toto', 'titi'], ['toto', 'titi']),
            ('toto\n\ntiti\n', ['toto', 'titi'], ['toto', '', 'titi']),
            ('toto\n\n\ttiti\n', ['toto', 'titi'], ['toto', '', '\ttiti']),
        )
        for (test_val, expected, expected_pref) in test_vals:
            self.assertEqual(expected, rf._split_lines(test_val, 7))
            self.assertEqual(expected_pref, rf._split_lines(rf._PREFIX + test_val, 7))

if __name__ == '__main__':
    import pytest
    pytest.main(['-x', '--pdb', __file__])
