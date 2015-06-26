#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import json
import urllib
import argparse
import subprocess

if 'DEVNULL' not in dir(subprocess):
    subprocess.DEVNULL = open('/dev/null', 'rw+b')

# Hashing algorithm: (command line, message digest size in bits)
_HASHES = {
          'MD5': (['md5sum', '--binary'], 128),
          'SHA-1': (['sha1sum', '--binary'], 160),
          'SHA-256': (['sha256sum', '--binary'], 256),
          'SHA-512': (['sha512sum', '--binary'], 512),
         }

def do_argparse():
    parser = argparse.ArgumentParser(description='Import VM images into glance, and verify checksum(s)')
    
    parser.add_argument('-f', '--fullcheck', action='store_true',
                       help='verify all available checksums, not just md5')
    parser.add_argument('files', metavar='FILE', type=argparse.FileType('r'), nargs='+',
                       help='a .json file describing a VM, from the StratusLab marketplace (https://marketplace.stratuslab.eu)')

    args = parser.parse_args()
    return args

def check_glance_availability():
    try:
        ret = subprocess.call(['glance', '--version'],
                              stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        if ret != 0:
            print("%s: Cannot execute 'glance', please check it is properly"
                  " installed." % (sys.argv[0],), file=sys.stderr)
            sys.exit(ret)
    except:
        print("%s: Cannot execute 'glance', please check it is properly"
              " installed, and available in your PATH environment "
              "variable." % (sys.argv[0],), file=sys.stderr)
        raise

def get_url(url):
    fn, hdrs = urllib.urlretrieve(url)
    return fn

def handle_one_file(f):
    tmp = json.loads(f.read())
    f.close()
    ret = {}
    if type(tmp) is dict:
        for val in tmp.values():
            # Early exit in case we found all interesting checksums
            if len(ret) == 5:
                return ret
            for key in val.keys():
                if key == 'http://mp.stratuslab.eu/slterms#location':
                    ret['url'] = val['http://mp.stratuslab.eu/slterms#location'][0]['value']
                elif key == "http://mp.stratuslab.eu/slreq#algorithm":
                    algo = val[key][0]['value']
                    ret[algo] = val['http://mp.stratuslab.eu/slreq#value'][0]['value']
    return ret

# VM images are gzip'ed, but checksums are for uncompressed files
def gunzip(fn):
    ret = subprocess.call(['gunzip', fn],
                          stdin=subprocess.DEVNULL,
                          stdout=subprocess.DEVNULL)
    if ret != 0:
        print('Failed to uncompress: ', fn)

# Compute message digest for given file name with the given algorithm
def get_hash(fn, hashing):
    p = subprocess.Popen(hashing[0] + [fn], stdout=subprocess.PIPE)
    out, err = p.communicate()
    ret = p.returncode
    if ret == 0:
        return out[:hashing[1]*2/8]
    return None

def main():
    args = do_argparse()
    check_glance_availability()
    for f in args.files:
        ret = handle_one_file(f)
        fn = get_url(ret['url'])
        gunzip(fn)
        base, ext = os.path.splitext(fn)
        h = get_hash(base, _HASHES['MD5'])
        print(ret)
        if (h == ret['MD5']):
            print('OK')
        else:
            print('WARNING: checksum does not match:', h)

if __name__ == '__main__':
    main()
