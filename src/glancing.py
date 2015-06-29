#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import json
import urllib
import urlparse
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

_GLANCE_CMD = ['glance']

# Handle CLI options
def do_argparse():
    parser = argparse.ArgumentParser(description='Import VM images into glance, and verify checksum(s)')

    parser.add_argument('-k', '--keep-temps', dest='keeptemps', action='store_true',
                       help='keep temporary VM image files')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='display additional information')
    parser.add_argument('-f', '--force', action='store_true',
                       help='force import into glance, even if checksum verification failed')
    parser.add_argument('-d', '--dry-run', dest='dryrun', action='store_true',
                       help='only download and verify checksums, do not import into glance')
    parser.add_argument('-c', '--check-all', dest='fullcheck', action='store_true',
                       help='verify all available checksums, not just md5')

    parser.add_argument('files', metavar='FILE', type=argparse.FileType('r'), nargs='+',
                       help='a .json file describing a VM, from the StratusLab marketplace (https://marketplace.stratuslab.eu)')

    args = parser.parse_args()
    return args

# Ensure we can run glance
def check_glance_availability(verbose=False):
    try:
        subprocess.check_call(_GLANCE_CMD,
                              stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except OSError as e:
        print("%s: Cannot execute '%s', please check it is properly"
              " installed, and available through your PATH environment "
              "variable." % (sys.argv[0], _GLANCE_CMD[0]), file=sys.stderr)
        if verbose:
            print(e)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("%s: '%s' does not run properly." % (sys.argv[0],
              _GLANCE_CMD[0]), file=sys.stderr)
        if verbose:
            print(e)
        sys.exit(e.returncode)

# Get uncompressed VM image file from the given url
def get_url(url):
    fn, hdrs = urllib.urlretrieve(url)
    gunzip(fn)
    base, ext = os.path.splitext(fn)
    return base

# Parse the metadata .json file, from the stratuslab marketplace
def get_metadata(f):
    tmp = json.loads(f.read())
    f.close()
    ret = {}
    if type(tmp) is dict:
        for val in tmp.values():
            # Early exit in case we found all interesting checksums and
            # the VM image file url
            if len(ret) == len(_HASHES) + 1:
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
        print('Failed to uncompress: ', fn, file=sys.stderr)

# Compute message digest for given file name with the given algorithm
def get_hash(fn, hashing):
    p = subprocess.Popen(hashing[0] + [fn], stdout=subprocess.PIPE)
    out, err = p.communicate()
    ret = p.returncode
    if ret == 0:
        return out[:hashing[1]*2/8]
    return None

# Import VM image into glance
def glance_import(base):
    pass

def main():
    args = do_argparse()
    if not args.dryrun:
        check_glance_availability(args.verbose)
    for f in args.files:
        ret = get_metadata(f)
        base = get_url(ret['url'])
        if args.verbose:
            print(f.name, ': downloaded image into :', base)
        verified = 0
        if (args.fullcheck):
            hashes = list(set(ret.keys()) - set(['url']))
        else:
            hashes = ['MD5']
        for hashfn in sorted(hashes):
            h = get_hash(base, _HASHES[hashfn])
            if h == ret[hashfn]:
                if args.verbose:
                    print(f.name, ': OK :', hashfn)
                verified += 1
            else:
                if args.verbose:
                    print(f.name, ': WARNING : checksum does not match', hashfn)
                    print(f.name, ': WARNING :     expected =', ret[hashfn])
                    print(f.name, ': WARNING :     computed =', h)
        if not args.dryrun:
            if args.force or len(hashes) == verified:
                glance_import(base)
        if not args.keeptemps:
            if args.verbose:
                print(f.name, ': deleting temporary file :', base)
            os.remove(base)

if __name__ == '__main__':
    main()
