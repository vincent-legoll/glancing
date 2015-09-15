#! /usr/bin/env python

'''Two classes implementing checksum computations with different methods:
- parallel block computation with python's hashlib
- sequential computation by execution of external programs, such as md5sum
  and its cousins.

For big files, parallel hashlib implementation beats serialized execution,
because the source file is only read once. It will also be nicer for the
operating system caches...
'''

import os
import sys
import hashlib
import collections

import utils

try:
    _HASH_ALGOS = hashlib.algorithms
except AttributeError:
    _HASH_ALGOS = hashlib.algorithms_guaranteed

# Mapping from algorithm to digest length
_HASH_TO_LEN = { hash_name: hashlib.__dict__[hash_name]().digest_size * 2 for hash_name in _HASH_ALGOS }

# Mapping from digest length to algorithm
_LEN_TO_HASH = { hashlib.__dict__[hash_name]().digest_size * 2: hash_name for hash_name in _HASH_ALGOS }

class multihash_hashlib(object):
    '''Compute multiple message digests in parallel, using python's hashlib
    '''

    def __init__(self, hash_names=_HASH_ALGOS, block_size=4096):
        self.data = {hash_name: hashlib.__dict__[hash_name]() for hash_name in hash_names}
        self.block_size = block_size

    def update(self, data):
        for algo in self.data.values():
            algo.update(data)

    def hexdigests(self):
        return {hash_name: hash_obj.hexdigest() for hash_name, hash_obj in self.data.iteritems()}

    def hash_file(self, filename):
        utils.block_read_filename(filename, self.update, self.block_size)

class multihash_serial_exec(object):
    '''Compute multiple message digests, one at a time, using external programs
    '''

    def __init__(self, hash_names=_HASH_ALGOS):
        self.hexdigests_data = {hash_name: '' for hash_name in hash_names}

    def hexdigests(self):
        return self.hexdigests_data

    def hash_file(self, filename):
        if not os.path.exists(filename):
            raise IOError('[Errno 2] No such file or directory: ' + filename)
        for hash_name in self.hexdigests_data.keys():
            h = self.get_hash(filename, hash_name)
            self.hexdigests_data[hash_name] = h

    # Compute message digest for given file name with the given algorithm
    def get_hash(self, fn, hash_name):
        cmd = [hash_name + 'sum', '--binary', fn]
        ok, _, out, _ = utils.run(cmd, out=True)
        if ok:
            return out[:_HASH_TO_LEN[hash_name]]
        return None

def multisum(digs):
    '''Emulate md5sum & its family, but computing all the message
       digests in parallel, only reading each file once.
    '''
    data = collections.OrderedDict()
    for (filename, digests) in digs.iteritems():
        for (hash_alg, digest) in digests.iteritems():
            fn = hash_alg.upper() + 'SUMS'
            lst_files = data.get(fn, [])
            lst_files.append(digest + '  ' + filename + '\n')
            data[fn] = lst_files
    for (filename, lines) in data.iteritems():
        if os.path.exists(filename):
            raise ValueError('ERROR: file already exists:', filename)
        with open(filename, 'wb') as fout:
            fout.writelines(lines)

def main(args=sys.argv[1:]):
    ret = collections.OrderedDict()
    for arg in args:
        mh = multihash_hashlib()
        mh.hash_file(arg)
        ret[arg] = mh.hexdigests()
    return ret

if __name__ == '__main__':
    multisum(main())
