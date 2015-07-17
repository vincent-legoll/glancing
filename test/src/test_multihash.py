#! /usr/bin/env python

import os
import sys
import unittest

from utils import get_local_path

# Setup PYTHONPATH for multihash
sys.path.append(get_local_path('..', '..', 'src'))

import multihash

class TestMultihash(unittest.TestCase):

    def multihash_test_files(self):
        files = ['/dev/null', 'random_1M.bin', 'random_5M.bin']
        for fn in files:
            local_path = get_local_path('..', 'data', fn)
            mhs = multihash.multihash_serial_exec()
            mhp = multihash.multihash_hashlib()
            mhs.hash_file(local_path)
            mhp.hash_file(local_path)
            self.assertEquals(mhs.hexdigests(), mhp.hexdigests())

    def multihash_test_nonexistent(self):
        mhs = multihash.multihash_serial_exec()
        with self.assertRaises(IOError):
            mhs.hash_file('/tmp/nonexistent')

        mhp = multihash.multihash_hashlib()
        with self.assertRaises(IOError):
            mhp.hash_file('/tmp/nonexistent')

    def multihash_test_string_hashlib(self):
        mh = multihash.multihash_hashlib()
        mh.update('toto')
        self.assertEquals(mh.hexdigests()['md5'], 'f71dbe52628a3f83a77ab494817525c6')
        mh.update('titi')
        self.assertEquals(mh.hexdigests()['md5'], '92fdff5b8595ef3f9ac0de664ce21532')

    def multihash_test_gethash_serial(self):
        mh = multihash.multihash_serial_exec()
        self.assertEquals(mh.get_hash('/dev/null', 'md5'), 'd41d8cd98f00b204e9800998ecf8427e')
        self.assertIsNone(mh.get_hash('/tmp/nonexistent', 'md5'))
        with self.assertRaises(OSError):
            mh.get_hash('/dev/null', 'nonexistent_hash_algo')

    def multihash_test_string_serial(self):
        mh = multihash.multihash_serial_exec()
        with open('test.txt', 'wb') as test_file:
            test_file.write('toto')
            test_file.flush()
            mh.hash_file('test.txt')
            self.assertEquals(mh.hexdigests()['md5'], 'f71dbe52628a3f83a77ab494817525c6')
            test_file.write('titi')
            test_file.flush()
            mh.hash_file('test.txt')
            self.assertEquals(mh.hexdigests()['md5'], '92fdff5b8595ef3f9ac0de664ce21532')
        os.remove('test.txt')
