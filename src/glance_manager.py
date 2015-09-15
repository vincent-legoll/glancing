#! /usr/bin/env python

from __future__ import print_function

import os
import re
import sys
import tempfile
import textwrap
import argparse

import utils
import glance
import glancing
import metadata
import multihash
import openstack_out

from utils import vprint

_DEFAULT_VMLIST_FILE = os.path.join('/', 'etc', 'glancing', 'vmlist')
_DEFAULT_SL_MARKETPLACE_URL_BASE = 'https://marketplace.stratuslab.eu/marketplace/metadata/'

# Handle CLI options
def do_argparse(sys_argv):
    desc_help = textwrap.dedent('''
        Manage the list of endorsed images to be distributed across all
        IdGC / France-Grilles sites.
    ''')
    parser = argparse.ArgumentParser(description=desc_help)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Display additional information')

    parser.add_argument('-l', '--vmlist', default=_DEFAULT_VMLIST_FILE,
                        help='List of endorsed VMs to put in glance')

    args = parser.parse_args(sys_argv)

    if args.verbose:
        utils.set_verbose(True)
        vprint('verbose mode')

    return args

def get_vmlist(vmlist_fn):
    ret = []
    with open(vmlist_fn, 'rb') as vmlist_f:
        for line in vmlist_f:
            ret.append(line)
    return ret

def get_glance_vmmap():
    ret = {}
    ids = glance.glance_ids()
    for vmid in ids:
        img = glance.glance_run('image-show', vmid)
        if img:
            vmmap = openstack_out.map_block(img)
            ret[vmmap['checksum']] = vmmap
            ret[vmmap['name']] = vmmap
    return ret

#~ $ glance image-show 0682c532-5c6b-4933-9657-9ea6bf93ce43
#~ +------------------+--------------------------------------+
#~ | Property         | Value                                |
#~ +------------------+--------------------------------------+
#~ | checksum         | 79b4436412283bb63c2cba4ac796bcd9     |
#~ | container_format | bare                                 |
#~ | created_at       | 2015-07-21T12:24:17                  |
#~ | deleted          | False                                |
#~ | disk_format      | raw                                  |
#~ | id               | 0682c532-5c6b-4933-9657-9ea6bf93ce43 |
#~ | is_public        | False                                |
#~ | min_disk         | 0                                    |
#~ | min_ram          | 0                                    |
#~ | name             | cirros-0.3.4-i386                    |
#~ | owner            | 0d932173c3504d0a93716329ceef753a     |
#~ | protected        | False                                |
#~ | size             | 12506112                             |
#~ | status           | active                               |
#~ | updated_at       | 2015-07-21T12:24:17                  |
#~ +------------------+--------------------------------------+
#~ --is-public [True|False]
    #~ Makes an image accessible for all the tenants (admin-only by default).
#~ --is-protected [True|False]
    #~ Prevents an image from being deleted.

def get_meta_file(vmid):
    # Get xml metadata file from StratusLab marketplace
    metadata_url_base = _DEFAULT_SL_MARKETPLACE_URL_BASE
    return glancing.get_url(metadata_url_base + vmid)

def handle_vm(vmid, vmmap):
    meta_file = get_meta_file(vmid)
    print(meta_file)
    meta = metadata.MetaStratusLabXml(meta_file)
    md = meta.get_metadata()
    new_md5 = md['checksums']['md5']

    if new_md5 in vmmap:
        vprint('Already in local glance: %s' % vmmap[new_md5]['name'])
        return

    name = meta.get_name()
    if name in vmmap:
        vprint('An image with the same name is already in glance, but md5 differ')
        if not glance.glance_rename(vmid, name + '_old'):
            return

    glance.glance_import(meta_file, md5=new_md5, name=name)

def main(sys_argv=sys.argv[1:]):
    args = do_argparse(sys_argv)
    if not args.vmlist or not os.path.exists(args.vmlist):
        return False
    vmmap = get_glance_vmmap()
    vmlist = get_vmlist(args.vmlist)
    for vmid in vmlist:
        handle_vm(vmid, vmmap)
    return True

if __name__ == '__main__':
    main()
