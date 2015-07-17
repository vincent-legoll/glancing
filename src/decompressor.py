#! /usr/bin/env python

import os
import sys
import bz2
import gzip

class FileExistsError(Exception):
    pass

_EXT_MAP = {
    '.gz': gzip.open,
    '.bz2': bz2.BZ2File,
}

class Decompressor(object):
    def __init__(self, filename, ext=None, block_size=4096):
        self.fin_name = filename
        self.block_size = block_size
        self.fout_name, sext = os.path.splitext(filename)

        if ext is not None and sext != ext:
            raise ValueError('Extension mismatch: ' + ext)
        if sext not in _EXT_MAP:
            raise NotSupportedError('Unknown file extension: ' + ext)
        if os.path.exists(self.fout_name):
            raise FileExistsError('File exists: ' + self.fout_name)
        self.opener = _EXT_MAP[sext]

    def doit(self, delete=False):
        with self.opener(self.fin_name, 'rb') as fin:
            with open(self.fout_name, 'wb+') as fout:
                block = fin.read(self.block_size)
                while (block):
                    fout.write(block)
                    block = fin.read(self.block_size)
        if delete:
            os.remove(self.fin_name)

def main():
    for fn in sys.argv[1:]:
        d = Decompressor(fn)
        d.doit()

if __name__ == '__main__':
    main()
