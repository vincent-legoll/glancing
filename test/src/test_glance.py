#! /usr/bin/env python

import os
import sys
import unittest

from tutils import get_local_path

# Setup PYTHONPATH for utils
sys.path.append(get_local_path('..', '..', 'src'))

import glance
import utils

utils.set_verbose(True)

class TestGlance(unittest.TestCase):

    def test_ok(self):
        self.assertTrue(glance.glance_ok())

    def test_exists_raise(self):
        with self.assertRaises(TypeError):
            glance.glance_exists(None)
        with self.assertRaises(TypeError):
            glance.glance_exists(True)
        with self.assertRaises(TypeError):
            glance.glance_exists(False)
        with self.assertRaises(TypeError):
            glance.glance_exists([])

    def test_exists_false(self):
        self.assertFalse(glance.glance_exists(''))
        self.assertFalse(glance.glance_exists('Nonexistent'))

    def test_glance_ids_single(self):
        self.assertEqual(set(), glance.glance_ids(None))
        self.assertEqual(set(), glance.glance_ids(True))
        self.assertEqual(set(), glance.glance_ids(False))
        self.assertEqual(set(), glance.glance_ids(''))
        self.assertEqual(set(), glance.glance_ids([]))

    def test_glance_ids_list_single(self):
        self.assertEqual(set(), glance.glance_ids([None]))
        self.assertEqual(set(), glance.glance_ids([True]))
        self.assertEqual(set(), glance.glance_ids([False]))
        self.assertEqual(set(), glance.glance_ids(['']))
        self.assertEqual(set(), glance.glance_ids([[]]))

    def test_glance_ids_list(self):
        self.assertEqual(set(), glance.glance_ids([None, True, False]))
        self.assertEqual(set(), glance.glance_ids(['', '']))

_IMG_NAME = 'test-glance-img'

class TestGlanceFixture(unittest.TestCase):

    def setUp(self):
        glance.glance_delete_all(_IMG_NAME, quiet=True)

    def tearDown(self):
        glance.glance_delete_all(_IMG_NAME, quiet=True)

class TestGlanceMain(TestGlanceFixture):

    def test_main_ok(self):
        self.assertFalse(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_import('/dev/null', name=_IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.main(['-d', _IMG_NAME]))
        self.assertFalse(glance.glance_exists(_IMG_NAME))

    def test_main_ok_verbose(self):
        self.assertFalse(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_import('/dev/null', name=_IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.main(['-v', '-d', _IMG_NAME]))
        self.assertFalse(glance.glance_exists(_IMG_NAME))

    def test_main_fail_wrong_param_delete(self):
        self.assertFalse(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_import('/dev/null', name=_IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_exists(_IMG_NAME))
        with self.assertRaises(SystemExit):
            with utils.devnull('stderr'):
                glance.main(['-d'])
        self.assertTrue(glance.glance_exists(_IMG_NAME))

    def test_main_fail_wrong_param_name(self):
        self.assertFalse(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_import('/dev/null', name=_IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_exists(_IMG_NAME))
        with self.assertRaises(SystemExit):
            with utils.devnull('stderr'):
                glance.main([_IMG_NAME])
        self.assertTrue(glance.glance_exists(_IMG_NAME))

class TestGlanceMisc(TestGlanceFixture):

    def test_exists_import(self):
        self.assertFalse(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_import('/dev/null', name=_IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_exists(_IMG_NAME))

    def test_delete_all(self):
        self.assertFalse(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_import('/dev/null', name=_IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_import('/dev/null', name=_IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_import('/dev/null', name=_IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_delete_all(_IMG_NAME))
        self.assertFalse(glance.glance_exists(_IMG_NAME))

    def test_delete(self):
        self.assertFalse(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_import('/dev/null', name=_IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_delete(_IMG_NAME))
        self.assertFalse(glance.glance_exists(_IMG_NAME))

    def test_download(self):
        _RND1M_FILE = get_local_path('..', 'data', 'random_1M.bin')
        _DL_ED_FILE = os.path.join('/', 'tmp', _IMG_NAME)

        if os.path.exists(_DL_ED_FILE):
            os.remove(_DL_ED_FILE)
        self.assertFalse(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_import(_RND1M_FILE, name=_IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_exists(_IMG_NAME))
        self.assertTrue(glance.glance_download(_IMG_NAME, _DL_ED_FILE))
        self.assertTrue(os.path.exists(_DL_ED_FILE))
        self.assertTrue(utils.run(['cmp', _RND1M_FILE, _DL_ED_FILE])[0])
        os.remove(_DL_ED_FILE)
        self.assertFalse(glance.glance_download('', _DL_ED_FILE))
        self.assertFalse(os.path.exists(_DL_ED_FILE))
