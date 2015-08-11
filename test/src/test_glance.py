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

class TestGlanceFixture(unittest.TestCase):

    def setUp(self):
        glance.glance_delete('test-glance-img', quiet=True)

    def tearDown(self):
        glance.glance_delete('test-glance-img', quiet=True)

    def test_exists(self):
        with self.assertRaises(TypeError):
            glance.glance_exists(None)
        with self.assertRaises(TypeError):
            glance.glance_exists(True)
        with self.assertRaises(TypeError):
            glance.glance_exists(False)
        self.assertFalse(glance.glance_exists(''))
        self.assertFalse(glance.glance_exists('test-glance-img'))
        glance.glance_import('/dev/null', name='test-glance-img')
        self.assertTrue(glance.glance_exists('test-glance-img'))

    def test_import(self):
        self.assertFalse(glance.glance_exists('test-glance-img'))
        self.assertTrue(glance.glance_import('/dev/null', name='test-glance-img'))
        self.assertTrue(glance.glance_exists('test-glance-img'))

    def test_delete(self):
        self.assertFalse(glance.glance_exists('test-glance-img'))
        glance.glance_import('/dev/null', name='test-glance-img')
        self.assertTrue(glance.glance_exists('test-glance-img'))
        glance.glance_delete('test-glance-img')
        self.assertFalse(glance.glance_exists('test-glance-img'))

    def test_download(self):
        _RND1M_FILE = get_local_path('..', 'data', 'random_1M.bin')
        self.assertFalse(glance.glance_exists('test-glance-img'))
        glance.glance_import(_RND1M_FILE, name='test-glance-img', diskformat='raw')
        self.assertTrue(glance.glance_exists('test-glance-img'))
        self.assertTrue(glance.glance_download('test-glance-img', '/tmp/test-glance-img'))
        self.assertTrue(utils.run(['cmp', _RND1M_FILE, '/tmp/test-glance-img'])[0])
        os.remove('/tmp/test-glance-img')
        self.assertFalse(glance.glance_download('', '/tmp/test-glance-img'))
