#! /usr/bin/env python

import hashlib
import subprocess

# Mapping from algorithm to digest length
_HASH_TO_LEN = {hash_name: hashlib.__dict__[hash_name]().digest_size * 2 for hash_name in hashlib.algorithms}

# Mapping from digest length to algorithm
_LEN_TO_HASH = {hashlib.__dict__[hash_name]().digest_size * 2: hash_name for hash_name in hashlib.algorithms}

class multihash_hashlib(object):
    '''Compute multiple message digests at once
    '''

    def __init__(self, hash_names=hashlib.algorithms, block_size=4096):
        self.data = {hash_name: hashlib.__dict__[hash_name]() for hash_name in hash_names}
        self.block_size = block_size

    def update(self, data):
        for algo in self.data.values():
            algo.update(data)

    def hexdigests(self):
        return {hash_name: hash_obj.hexdigest() for hash_name, hash_obj in self.data.iteritems()}

    def hash_file(self, filename):
        with open(filename, 'rb') as f:
            block = f.read(self.block_size)
            while (block):
                self.update(block)
                block = f.read(self.block_size)

class multihash_serial_exec(object):
    '''Compute multiple message digests, one at a time, using external programs
    '''

    def __init__(self, hash_names=hashlib.algorithms):
        self.hexdigests_data = {hash_name: '' for hash_name in hash_names}

    def hexdigests(self):
        return self.hexdigests_data

    def hash_file(self, filename):
        for hash_name in self.hexdigests_data.keys():
            h = self.get_hash(filename, hash_name)
            self.hexdigests_data[hash_name] = h

    # Compute message digest for given file name with the given algorithm
    def get_hash(self, fn, hash_name):
        p = subprocess.Popen([hash_name + 'sum', '--binary', fn], stdout=subprocess.PIPE)
        out, err = p.communicate()
        ret = p.returncode
        if ret == 0:
            return out[:_HASH_TO_LEN[hash_name]]
        return None

def test_serial_exec():
    import sys
    print 'test_serial_exec()'
    for arg in sys.argv[1:]:
        mh = multihash_serial_exec()
        mh.hash_file(arg)
        print mh.hexdigests()

def test_hashlib():
    import sys
    print 'test_hashlib()'
    for arg in sys.argv[1:]:
        mh = multihash_hashlib()
        mh.hash_file(arg)
        print mh.hexdigests()

    print
    mh = multihash_hashlib()
    mh.update('toto')
    print mh.hexdigests()
    mh.update('titi')
    print mh.hexdigests()

def main():
    test_serial_exec()
    print
    test_hashlib()

if __name__ == '__main__':
    main()
