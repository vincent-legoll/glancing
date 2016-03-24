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
            'md5': 'b1e40b428a6f711c6921926a579bac36',
            'sha1': '169e4ad142d707e7d0eb1962d32ad00fcb2d6dcf',
            'sha224': '12fc7c41885c375df0434d33e6811eb1cb66163edec5de8fdf162711',
            'sha256': '80983784e896dbc9fd8d499d302996d005f7efdbbd4511b0052673ca9457a9ea',
            'sha384': '3cafc50f51bde82a7994a5227e8213874ea689e20abc12bb2917ff9041b3f227c88fc32bc2a92adfe1fa76eaaea23d3c',
            'sha512': '15dd9fa60bf907a1be9282f67ff10bd52515332488c81fa606f806380d0b0e2a2b2604ab3235ce31e6ab29d4fed751021103c3a4d35c4075f1d5b11d26a163fc',
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
