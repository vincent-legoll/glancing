#! /usr/bin/env python

import os
import sys
import shutil
import unittest

from tutils import get_local_path

# Setup PYTHONPATH for decompressor
sys.path.append(get_local_path('..', '..', 'src'))

import decompressor

_TEST_FILES = ['random_1M_bz2.bin.bz2', 'random_1M_gz.bin.gz', 'random_1M_zip.bin.zip']

class DecompressorSimpleTest(unittest.TestCase):

    testdir = '/tmp/TestDecompressorSimple'

    def setUp(self):
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)
        os.mkdir(self.testdir)
        for fn in _TEST_FILES:
            local_path = get_local_path('..', 'data', fn)
            shutil.copy(local_path, self.testdir)

    def tearDown(self):
        shutil.rmtree(self.testdir)

    def test_decompressor_simple(self):
        for fn in _TEST_FILES:
            local_path = os.path.join(self.testdir, fn)
            d = decompressor.Decompressor(local_path)
            d.doit()
            name, sext = os.path.splitext(local_path)
            self.assertTrue(os.path.exists(name))
            self.assertTrue(os.path.exists(local_path))

    def test_decompressor_simple_delete(self):
        for fn in _TEST_FILES:
            local_path = os.path.join(self.testdir, fn)
            d = decompressor.Decompressor(local_path)
            d.doit(delete=True)
            name, sext = os.path.splitext(local_path)
            self.assertTrue(os.path.exists(name))
            self.assertFalse(os.path.exists(local_path))

    def test_decompressor_main(self):
        test_files = [os.path.join(self.testdir, fn) for fn in _TEST_FILES]
        self.assertTrue(decompressor.main(test_files))

class DecompressorErrorsTest(unittest.TestCase):

    def test_decompressor_good_ext(self):
        for ext in decompressor._EXT_MAP:
            with self.assertRaises(ValueError):
                d = decompressor.Decompressor(os.devnull, ext)
            with self.assertRaises(ValueError):
                d = decompressor.Decompressor('/tmp/nonexistent', ext)

            d = decompressor.Decompressor('/tmp/nonexistent' + ext)

    def test_decompressor_bad_ext_param(self):
        with self.assertRaises(ValueError):
            d = decompressor.Decompressor(os.devnull, '.txt')

    def test_decompressor_bad_ext(self):
        with self.assertRaises(decompressor.FileExtensionError):
            d = decompressor.Decompressor('/tmp/nonexistent.txt')

    def test_decompressor_nonexistent(self):
        with self.assertRaises(decompressor.FileExtensionError):
            d = decompressor.Decompressor('/tmp/nonexistent')
