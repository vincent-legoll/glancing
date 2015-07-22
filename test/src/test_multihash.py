#! /usr/bin/env python

import os
import sys
import unittest

from tutils import get_local_path

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

    def multihash_test_main(self):
        devnull_checksums = {
            'md5': 'd41d8cd98f00b204e9800998ecf8427e',
            'sha1': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
            'sha224': 'd14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f',
            'sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            'sha384': '38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1da274edebfe76f65fbd51ad2f14898b95b',
            'sha512': 'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e',
        }
        random_checksums = {
            'md5': 'bbca8754698f5eafc1d709611ee768e3',
            'sha1': '40ce448e9c72cb3daae50902b6b08372feed46c6',
            'sha224': '006b8bd373007dd71bbb23788fbf7cdd585671ace5da4b11730b7d3c',
            'sha256': '4b00863c104b00012f6adb6580f92c04b0b25cae36a4da289e4f528587b55a48',
            'sha384': '528e21e7f2a439309a46147b8070c4256d74f4bfb56acdede004f5736b7c32c43421a43c26e608ac0dd45bc3f768b65a',
            'sha512': '694ad2de81ea9dadf6f08dce8c0f52aaed5fadca7a98055e69b3bed2a733193a1557d6a75a50f01c064af5761385d95cc3cfe6eebf1a7e8fc6ede1d8f1991ae6',
        }
        files_to_hash = ['/dev/null', get_local_path('..', 'data', 'random_1M.bin')]
        self.assertEqual([devnull_checksums, random_checksums], multihash.main(files_to_hash))
