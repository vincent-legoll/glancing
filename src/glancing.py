#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import json
import urllib
import textwrap
import urlparse
import argparse

import utils
import glance
import multihash
import decompressor

from utils import vprint
from metadata import MetaStratusLabJson, MetaStratusLabXml

# Handle CLI options
def do_argparse(sys_argv):
    parser = argparse.ArgumentParser(description='Import VM images into OpenStack glance image registry, verify checksum(s), backup old images, etc...')

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
    parser_imag = subparsers.add_parser('image', help='import a VM image from a local file')
    parser_url = subparsers.add_parser('url', help='import a VM image from a network location (URL)')
    parser_json = subparsers.add_parser('json', help='import a VM image described by a metadata file (from the StratusLab marketplace) (https://marketplace.stratuslab.eu)')
    parser_market = subparsers.add_parser('market', help='import a VM image described by an ID (from the StratusLab marketplace) (https://marketplace.stratuslab.eu)')

    # StratusLab marketplace direct from UUID
    parser_market.add_argument('market_id', metavar='UUID',
                               help='a VM image ID from StratusLab marketplace')
    parser_market.add_argument('-k', '--keep-temps', dest='keeptemps', action='store_true',
                               help='keep temporary VM image & other files')

    # JSON-specific options
    parser_json.add_argument('jsonfile', metavar='FILE',
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

    args = parser.parse_args(sys_argv)

    if args.verbose:
        utils.set_verbose(True)
        vprint('verbose mode')

    return args

# Get uncompressed VM image file from the given url
def get_url(url):
    try:
        fn, hdrs = urllib.urlretrieve(url)
    except IOError as e:
        return None
    return fn

# Check all message digests of the image file
def check_digests(local_image_file, metadata, replace_bads=False):
    verified = 0
    hashes = metadata['checksums']
    mh = multihash.multihash_hashlib(hashes)
    mh.hash_file(local_image_file)
    hds = mh.hexdigests()
    for hashfn in sorted(hashes):
        digest_computed = hds[hashfn]
        digest_expected = hashes[hashfn]
        if digest_computed.lower() == digest_expected.lower():
            verified += 1
            vprint('%s: %s: OK' % (local_image_file, hashfn))
        else:
            vprint('%s: %s: expected: %s' % (local_image_file, hashfn, digest_expected))
            vprint('%s: %s: computed: %s' % (local_image_file, hashfn, digest_computed))
            if replace_bads:
                hashes[hashfn] = digest_computed
    return verified

_BACKUP_DIR = os.path.join('/', 'tmp', 'glancing')

def backup_dir():
    if not os.path.exists(_BACKUP_DIR):
        os.mkdir(_BACKUP_DIR)
    elif not os.path.isdir(_BACKUP_DIR):
        vprint(_BACKUP_DIR + ' exists but is not a direstory, sorry cannot backup old image...')

def main(sys_argv=sys.argv[1:]):

    # Handle CLI arguments
    args = do_argparse(sys_argv)

    # Check glance availability early
    if not args.dryrun and not glance.glance_ok():
        vprint('glance problem')
        return False

    # Prepare VM image metadata
    if args.image_type == 'market':
        # Get xml metadata file from StratusLab marketplace
        metadata_url = 'https://marketplace.stratuslab.eu/marketplace/metadata/' + args.market_id
        local_metadata_file = get_url(metadata_url)
        metadata = MetaStratusLabXml(local_metadata_file).get_metadata()
    elif args.image_type == 'json':
        metadata = MetaStratusLabJson(args.jsonfile).get_metadata()
    else:
        metadata = {'checksums': {}, 'format': 'raw'}

    # Ensure we have something to work on
    if not metadata:
        vprint('Cannot retrieve metadata')
        return False

    # Retrieve image in a local file
    if args.image_type == 'image':
        # Already a local file
        local_image_file = args.imagefile
        if not os.path.exists(local_image_file):
            vprint(local_image_file + ': file not found')
            return False
    else:
        # Download from network location
        if args.image_type in ('json', 'market'):
            url = metadata['location']
        elif args.image_type == 'url':
            url = args.url
        local_image_file = get_url(url)
        if not local_image_file or not os.path.exists(local_image_file):
            vprint('cannot download from: ' + url)
            return False
        vprint(local_image_file + ': downloaded image from: ' + url)

    # VM images are compressed, but checksums are for uncompressed files
    if 'compression' in metadata and metadata['compression']:
        chext = '.' + metadata['compression']
        d = decompressor.Decompressor(local_image_file, ext=chext)
        d.doit(delete=True)
        local_image_file, ext = os.path.splitext(local_image_file)
        vprint(local_image_file + ': uncompressed file')

    # Choose VM image name
    name = args.name
    if name is None:
        if args.image_type == 'image':
            name, ext = os.path.splitext(os.path.basename(local_image_file))
        elif args.image_type == 'url':
            name, ext = os.path.splitext(os.path.basename(urlparse.urlsplit(args.url)[2]))
        elif args.image_type in ('json', 'market'):
            name = '%s-%s-%s' % (metadata['os'], metadata['os-version'], metadata['os-arch'])
    vprint(local_image_file + ': VM image name: ' + name)

    # Populate metadata message digests to be verified
    if args.image_type not in ('json', 'market') and args.digests:
        for dig in filter(None, args.digests.split(':')):
            dig_len = len(dig)
            if dig_len in multihash._LEN_TO_HASH:
                halg = multihash._LEN_TO_HASH[dig_len]
                if halg in metadata['checksums']:
                    if dig == metadata['checksums'][halg]:
                        vprint('duplicate digest, computing only once: ' + dig)
                    else:
                        vprint('conflicting digests: ' + dig + ':' + metadata['checksums'][halg])
                        return False
                else:
                    metadata['checksums'][halg] = dig
            else:
                vprint('unrecognized digest: ' + dig)
                return False

    # Verify image size
    size_ok = True
    if 'bytes' in metadata:
        size_expected = int(metadata['bytes'])
        size_actual = os.path.getsize(local_image_file)
        size_ok = size_expected == size_actual

        if size_ok:
            vprint('%s: size: OK' % (local_image_file,))
        else:
            vprint('%s: size: expected: %d' % (local_image_file, size_expected))
            vprint('%s: size:   actual: %d' % (local_image_file, size_actual))
            if not args.force:
                return False

    # Verify image checksums
    verified = 0
    if size_ok:
        if len(metadata['checksums']) > 0:
            vprint(local_image_file + ': verifying checksums')
            verified = check_digests(local_image_file, metadata, args.force)
        elif args.image_type not in ('json', 'market'):
            vprint(local_image_file + ': no checksum to verify (forgot "-s" CLI option ?)')
        else:
            vprint(local_image_file + ': no checksum to verify found in metadata...')
    else:
        if args.force:
            vprint(local_image_file + ': size differ, but forcing the use of recomputed md5')
            metadata['checksums'] = { 'md5': '0' * 32 }
            check_digests(local_image_file, metadata, args.force)
        else:
            vprint(local_image_file + ': size differ, not verifying checksums')

    # If image already exists, download it to backup directory
    if not args.dryrun and glance.glance_exists(name):
        backup_dir()
        fn_local = os.path.join(_BACKUP_DIR, name)
        ok = glance.glance_download(name, fn_local)
        if not ok:
            return False
        glance.glance_delete(name, quiet=(not utils.get_verbose()))

    # Import image into glance
    if not args.dryrun:
        if (size_ok and len(metadata['checksums']) == verified) or args.force:
            vprint(local_image_file + ': importing into glance as "%s"' % name or '')
            md5 = metadata['checksums'].get('md5', None)
            ret = glance.glance_import(local_image_file, md5, name, metadata['format'])
            if not ret:
                return False
        else:
            return False
    else:
        if not args.force and (not size_ok or not len(metadata['checksums']) == verified):
            return False

    # Keep downloaded image file
    if not args.image_type == 'image' and not args.keeptemps:
        vprint(local_image_file + ': deleting temporary file')
        os.remove(local_image_file)

    # That's all folks !
    return True

if __name__ == '__main__':
    main()
