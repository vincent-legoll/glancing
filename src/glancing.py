#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import json
import urllib
import textwrap
import urlparse
import argparse
import subprocess

import metadata
import multihash
import decompressor

if 'DEVNULL' not in dir(subprocess):
    subprocess.DEVNULL = open('/dev/null', 'rw+b')

_GLANCE_CMD = ['glance']

_VERBOSE = False

def vprint(msg):
    if _VERBOSE:
        print("%s: %s" % (sys.argv[0], msg))

# Handle CLI options
def do_argparse():
    parser = argparse.ArgumentParser(description='Import VM images into glance, and verify checksum(s)')

    # Global options
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='display additional information')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--force', action='store_true',
                       help='import image into glance even if checksum verification failed')
    group.add_argument('-d', '--dry-run', dest='dryrun', action='store_true',
                       help='do not import image into glance')

    parser.add_argument('-n', '--name', dest='name', default=None,
                       help='glance name of the image. Default value derived from image file name.')

    # Sub parsers for local image, url or stratuslab json metadata
    subparsers = parser.add_subparsers(dest='image_type')
    parser_imag  = subparsers.add_parser('image', help='import a VM image from a local file')
    parser_url   = subparsers.add_parser('url',   help='import a VM image from a network location (URL)')
    parser_json  = subparsers.add_parser('json',  help='import a VM image described by a json metadata file from the StratusLab marketplace (https://marketplace.stratuslab.eu)')

    # JSON-specific options
    parser_json.add_argument('jsonfile', metavar='FILE', type=argparse.FileType('r'),
                       help='a .json metadata file describing a VM image')
    parser_json.add_argument('-k', '--keep-temps', dest='keeptemps', action='store_true',
                       help='keep temporary VM image files')

    digests_help = textwrap.dedent('''
            colon-separated list of message digests of the image, algorithms are deduced 
            from checksum lengths, for example, an MD5 (32 chars) and a SHA-1 (40 chars):
            "3bea57666cdead13f0ed4a91beef2b98:1b5229d5dad92bc6662553be01608af2180eafbe"
        ''').strip()

    # Local file-specific options
    parser_imag.add_argument(dest='imagefile', metavar='FILE',
                       help='a local VM image file, raw format')
    parser_imag.add_argument('-s', '--digests', dest='digests', help=digests_help)

    # Network url-specific options
    parser_url.add_argument(dest='url', metavar='URL',
                       help='a network url VM image to download, raw format')
    parser_url.add_argument('-k', '--keep-temps', dest='keeptemps', action='store_true',
                       help='keep temporary VM image files')
    parser_url.add_argument('-s', '--digests', dest='digests', help=digests_help)

    args = parser.parse_args()

    if args.verbose:
        global _VERBOSE
        _VERBOSE = True
        vprint('verbose mode')

    return args

# Ensure we can run glance
def check_glance_availability():
    try:
        subprocess.check_call(_GLANCE_CMD,
                              stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except OSError as e:
        print("%s: Cannot execute '%s', please check it is properly"
              " installed, and available through your PATH environment "
              "variable." % (sys.argv[0], _GLANCE_CMD[0]), file=sys.stderr)
        vprint(e)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("%s: '%s' does not run properly." % (sys.argv[0],
              _GLANCE_CMD[0]), file=sys.stderr)
        vprint(e)
        sys.exit(e.returncode)

# Get uncompressed VM image file from the given url
def get_url(url):
    fn, hdrs = urllib.urlretrieve(url)
    return fn

# Check all message digests of the image file
def check_digests(local_image_file, metadata):
    verified = 0
    md5 = None
    hashes = metadata['checksums']
    mh = multihash.multihash_hashlib(hashes)
    mh.hash_file(local_image_file)
    hds = mh.hexdigests()
    for hashfn in sorted(hashes):
        digest_computed = hds[hashfn]
        if hashfn == 'md5':
            md5 = digest_computed
        digest_expected = hashes[hashfn]
        if digest_computed.lower() == digest_expected.lower():
            verified += 1
            vprint('%s: %s: OK' % (local_image_file, hashfn))
        else:
            vprint('%s: %s: expected: %s' % (local_image_file, hashfn, digest_expected))
            vprint('%s: %s: computed: %s' % (local_image_file, hashfn, digest_computed))
    return verified, md5

# Import VM image into glance
def glance_import(base, md5=None, name=None, diskformat=None):
    cmd = _GLANCE_CMD + ['image-create', '--container-format', 'bare', '--file', base]
    if diskformat is not None:
        cmd += ['--disk-format', diskformat]
    if name is not None:
        cmd += ['--name', name]
    if md5 is not None:
        cmd += ['--checksum', md5]
    ret = subprocess.call(cmd,
                          stdin=subprocess.DEVNULL,
                          stdout=subprocess.DEVNULL)
    if ret != 0:
        print('%s: Failed to import image into glance' % (sys.argv[0],), file=sys.stderr)
    return ret

def main():
    args = do_argparse()

    # Check glance availability early
    if not args.dryrun:
        check_glance_availability()

    # Prepare VM image metadata
    if args.image_type == 'json':
        metadata = MetaStratusLab(args.jsonfile).get_metadata()
    else:
        metadata = {'checksums': {}, 'diskformat': 'raw'}

    # Retrieve image in a local file
    if args.image_type == 'image':
        # Already a local file
        local_image_file = args.imagefile
        if not os.path.exists(local_image_file):
            vprint(local_image_file + ': file not found')
            sys.exit(1)
    else:
        # Download from network location
        if args.image_type == 'json':
            local_image_file = get_url(metadata['url'])
        elif args.image_type == 'url':
            local_image_file = get_url(args.url)
        vprint(local_image_file + ': downloaded image')

    # Uncompress downloaded file
    # VM images are compressed, but checksums are for uncompressed files
    if 'compression' in metadata:
        chext = '.' + metadata['compression']
        d = decompressor.decompressor(local_image_file, ext=chext)
        d.doit(delete=True)
        local_image_file, ext = os.path.splitext(local_image_file)
        vprint(local_image_file + ': uncompressed file')

    # Choose VM image name
    name = args.name
    if name is None:
        if args.image_type == 'image':
            name, ext = os.path.splitext(os.path.basename(local_image_file))
        elif args.image_type == 'url':
            name, ext = os.path.splitext(urlparse.urlsplit(args.url)[2])
        else:
            name = '%s-%s-%s' % (metadata['ostype'], metadata['osver'], metadata['osarch'])
    vprint(local_image_file + ': VM image name: ' + name)

    # Populate metadata message digests to de verified
    if args.image_type != 'json' and args.digests:
        for dig in filter(args.digests.split(':')):
            dig_len = len(dig)
            if dig_len in multihash._LEN_TO_HASH:
                halg = multihash._LEN_TO_HASH[dig_len]
                metadata['checksums'][halg] = dig
            else:
                vprint('unrecognized digest : ' + dig)

    # Verify image size
    size_ok = True
    if 'size' in metadata:
        size_expected = int(metadata['size'])
        size_actual = os.path.getsize(local_image_file)
        size_ok = size_expected == size_actual

        if size_ok:
            vprint('%s: size: OK' % (local_image_file,))
        else:
            vprint('%s: size: expected: %d' % (local_image_file, size_expected))
            vprint('%s: size:   actual: %d' % (local_image_file, size_actual))

    # Verify image checksums
    if size_ok:
        if len(metadata['checksums']) > 0:
            vprint(local_image_file + ': verifying checksums')
            verified, md5 = check_digests(local_image_file, metadata)
        elif args.image_type != 'json':
            vprint(local_image_file + ': no checksum to verify (forgot "-s" CLI option ?)')
        else:
            vprint(local_image_file + ': no checksum to verify found in metadata file...')
    else:
        vprint(local_image_file + ': size differ, not verifying checksums')

    # Import image into glance
    if not args.dryrun:
        if (size_ok and len(metadata['checksums']) == verified) or args.force:
            vprint(local_image_file + ': importing into glance as "%s"' % name or '')
            glance_import(local_image_file, md5, name, metadata['diskformat'])

    # Keep downloaded image file
    if not args.image_type == 'image' and not args.keeptemps:
        vprint(local_image_file + ': deleting temporary file')
        os.remove(local_image_file)

if __name__ == '__main__':
    main()
