#! /usr/bin/env python

import os
import sys
import glob
import unittest

from tutils import local_pythonpath, get_local_path

# Setup project-local PYTHONPATH
local_pythonpath('..', '..', 'src')

import utils
import multihash

class MultihashTest(unittest.TestCase):

    def test_multihash_files(self):
        files = [os.devnull, 'random_1M.bin', 'random_5M.bin']
        for fn in files:
            local_path = get_local_path('..', 'data', fn)
            mhs = multihash.multihash_serial_exec()
            mhp = multihash.multihash_hashlib()
            mhs.hash_file(local_path)
            mhp.hash_file(local_path)
            self.assertEquals(mhs.hexdigests(), mhp.hexdigests())

    def test_multihash_nonexistent(self):
        mhs = multihash.multihash_serial_exec()
        with self.assertRaises(IOError):
            mhs.hash_file('/tmp/nonexistent')

        mhp = multihash.multihash_hashlib()
        with self.assertRaises(IOError):
            mhp.hash_file('/tmp/nonexistent')

    def test_multihash_string_hashlib(self):
        mh = multihash.multihash_hashlib()
        mh.update('toto')
        self.assertEquals(mh.hexdigests()['md5'], 'f71dbe52628a3f83a77ab494817525c6')
        mh.update('titi')
        self.assertEquals(mh.hexdigests()['md5'], '92fdff5b8595ef3f9ac0de664ce21532')

    def test_multihash_gethash_serial(self):
        mh = multihash.multihash_serial_exec()
        self.assertEquals(mh.get_hash(os.devnull, 'md5'), 'd41d8cd98f00b204e9800998ecf8427e')
        self.assertIsNone(mh.get_hash('/tmp/nonexistent', 'md5'))

    def test_multihash_string_serial(self):
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

class MultihashTestGetHashSerial(unittest.TestCase):

    def setUp(self):
        self._v = utils.get_verbose()
        utils.set_verbose(True)

    def tearDown(self):
        utils.set_verbose(self._v)

    def test_multihash_gethash_serial_nonexistent_hash(self):
        mh = multihash.multihash_serial_exec()
        with utils.stringio() as output:
            with utils.redirect('stdout', output):
                nonexistent_hash = 'nonexistent_hash_algo'
                self.assertFalse(mh.get_hash(os.devnull, nonexistent_hash))
                out = ("%s: '%s%s': Cannot execute, please check it is properly"
                       " installed, and available through your PATH environment "
                       "variable.\n%s: [Errno 2] No such file or directory\n" %
                       (sys.argv[0], nonexistent_hash, 'sum', sys.argv[0]))
                self.assertEqual(output.getvalue(), out)

class MultihashTestMain(unittest.TestCase):

    def setUp(self):
        devnull_checksums = {
            'md5': 'd41d8cd98f00b204e9800998ecf8427e',
            'sha1': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
            'sha224': 'd14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f',
            'sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            'sha384': '38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1da274edebfe76f65fbd51ad2f14898b95b',
            'sha512': 'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e',
        }
        random_checksums = {
            'md5': '25cc288d4cead968ebe5c9fa3c4f9991',
            'sha1': '4245f235023adb28e25d9130a2063c5f35594cd8',
            'sha224': '6b636c9320f6574e6d33c087969b3de4f2c8983fc568e09ebadf0729',
            'sha256': 'd608c014160b577ffd6a7aa8b048cdf3afcdbc23f186dc30646a2b9cfc481120',
            'sha384': '4f51eaa6864f9e5079885a3ac30565581522669bd89e42d5a479433d897a1bf222337ae46125575c969fbc2b78c60e86',
            'sha512': 'd91fa3b083266ba7a651570acc4803e07e1910bcacceae303eb3684e4119907170888997cc13aeea2effa823d51b3dff965800942893ef7db8513cb339e55ae6',
        }
        self.files_to_hash = [os.devnull, get_local_path('..', 'data', 'random_1M.bin')]
        self.expected = dict(zip(self.files_to_hash, [devnull_checksums, random_checksums]))
        self.computed = multihash.main(self.files_to_hash)

    def test_multihash_main(self):
        self.assertEqual(self.expected, self.computed)

    def test_multihash_multisum(self):
        ok, ret, out, err = utils.run(['md5sum'] + self.files_to_hash, out=True)
        self.assertTrue(ok)
        with utils.tempdir():
            multihash.multisum(self.computed)
            with open('MD5SUMS', 'rb') as md5f:
                self.assertEqual(md5f.read(), out)
