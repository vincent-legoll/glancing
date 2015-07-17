#! /usr/bin/env python

import os
import sys

from utils import get_local_path

# Setup PYTHONPATH for multihash
sys.path.append(get_local_path('..', '..', 'src'))

import multihash

def multihash_test_files():
    files = ['random_1M.bin', 'random_5M.bin']
    for fn in files:
        local_path = get_local_path('..', 'data', fn)
        mhs = multihash.multihash_serial_exec()
        mhp = multihash.multihash_hashlib()
        mhs.hash_file(local_path)
        mhp.hash_file(local_path)
        assert mhs.hexdigests() == mhp.hexdigests()

def multihash_test_string_hashlib():
    mh = multihash.multihash_hashlib()
    mh.update('toto')
    assert mh.hexdigests()['md5'] == 'f71dbe52628a3f83a77ab494817525c6'
    mh.update('titi')
    assert mh.hexdigests()['md5'] == '92fdff5b8595ef3f9ac0de664ce21532'

def multihash_test_string_serial():
    mh = multihash.multihash_serial_exec()
    with open('test.txt', 'wb') as test_file:
        test_file.write('toto')
        test_file.flush()
        mh.hash_file('test.txt')
        assert mh.hexdigests()['md5'] == 'f71dbe52628a3f83a77ab494817525c6'
        test_file.write('titi')
        test_file.flush()
        mh.hash_file('test.txt')
        assert mh.hexdigests()['md5'] == '92fdff5b8595ef3f9ac0de664ce21532'
    os.remove('test.txt')
