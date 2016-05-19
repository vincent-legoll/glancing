#! /usr/bin/env python

import os
import sys
import bz2
import gzip
import zipfile

import utils

class DecompressorError(Exception):
    pass

def zip_opener(fn, _):
    zf = zipfile.ZipFile(fn, 'r')
    unfn, _ = os.path.splitext(fn)
    return zf.open(os.path.basename(unfn))

_EXT_MAP = {
    '.gz': gzip.open,
    '.bz2': bz2.BZ2File,
    '.zip': zip_opener,
}

class Decompressor(object):
    '''A class to handle differently-compressed file formats in an
    uniform way.
    '''

    def __init__(self, filename, ext=None, block_size=4096):

        if not os.path.exists(filename):
            raise DecompressorError('File does not exist: ' + filename)

        self.fin_name = filename
        self.block_size = block_size
        self.fout_name, sext = os.path.splitext(filename)

        if ext is not None and sext and sext != ext:
            raise DecompressorError('Extension mismatch: ' + sext + ' != ' + ext)
        if sext:
            if sext not in _EXT_MAP:
                raise DecompressorError('Unknown file extension: ' + str(ext))
        elif ext is None:
            raise DecompressorError('No file extension, and no '
                'decompression algorithm given: ' + filename)
        else:
            if ext not in _EXT_MAP:
                raise DecompressorError('No file extension, and unknown'
                    ' decompression algorithm given: ' + filename)
            self.fout_name += '_uncompressed'
        if os.path.exists(self.fout_name):
            raise DecompressorError('File exists: ' + self.fout_name)
        self.opener = _EXT_MAP[sext or ext]

    def doit(self, delete=False):
        ret = True
        try:
            with self.opener(self.fin_name, 'rb') as fin:
                delout = False
                try:
                    with open(self.fout_name, 'wb') as fout:
                        try:
                            utils.block_read_filedesc(fin, fout.write, self.block_size)
                        except IOError as exc:
                            if exc not in utils.Exceptions(IOError('Not a gzipped file')):
                                raise exc
                            delout = True
                            ret = False
                    if delout:
                        os.remove(self.fout_name)
                except IOError:
                    ret = False
        except Exception:
            ret = False

        if delete:
            os.remove(self.fin_name)
        return ret, self.fout_name

def main(args=sys.argv[1:]):
    for fn in args:
        d = Decompressor(fn)
        d.doit()
    return True

if __name__ == '__main__':
    main()
