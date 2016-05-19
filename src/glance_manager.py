#! /usr/bin/env python

''' Utility script to automatically distribute cloud images from the
France Grilles marketplace.
'''

from __future__ import print_function

import os
import sys
import textwrap
import argparse

import utils
import glance
import glancing
import metadata
import openstack_out

from utils import vprint

_DEFAULT_VMLIST_FILE = os.path.join('/', 'etc', 'glancing', 'vmlist')
_DEFAULT_SL_MARKETPLACE_URL_BASE = 'https://marketplace.stratuslab.eu/marketplace/metadata/'

def do_argparse(sys_argv):
    '''Handle CLI options
    '''
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
    '''Get list of StratusLab ID of images to download
    '''
    ret = []
    with open(vmlist_fn, 'rb') as vmlist_f:
        for line in vmlist_f:
            ret.append(line)
    return ret

def get_glance_images():
    '''Get info about images already in glance
    '''
    ret = {}
    ids = glance.glance_ids()
    for vmid in ids:
        img = glance.glance_show(vmid)
        if img:
            vmmap = openstack_out.map_block(img)
            ret[vmmap['checksum']] = vmmap
            ret[vmmap['name']] = vmmap
    return ret

def get_meta_file(vmid):
    '''Retrieve image metadata from StratusLab marketplace, in XML format
    '''
    # Get xml metadata file from StratusLab marketplace
    metadata_url_base = _DEFAULT_SL_MARKETPLACE_URL_BASE
    fn_meta = glancing.get_url(metadata_url_base + vmid)
    os.rename(fn_meta, fn_meta + '.xml')
    return fn_meta + '.xml'

def handle_vm(vmid, vmmap):
    '''Handle one image given by its SL marketplace ID
    '''
    vprint('handle_vm(%s)' % vmid)
    meta_file = get_meta_file(vmid)
    meta = metadata.MetaStratusLabXml(meta_file)
    mdata = meta.get_metadata()

    new_md5 = mdata['checksums']['md5']
    name = mdata['title']

    if new_md5 in vmmap:
        vprint('An image with the same MD5 is already in glance: ' + vmid)
        diff = False

        # Check name
        oldn = vmmap[new_md5]['name']
        newn = name
        if oldn != newn:
            vprint("But names differ, old: %s, new: %s" % (oldn, newn))
            diff = True

        # Check Version
        oldv = vmmap[new_md5]['version']
        newv = mdata['version']
        if oldv != newv:
            vprint("But versions differ, old: %s, new: %s" % (oldv, newv))
            diff = True

        # Which one is the good one ? Let the admin sort it out...
        if diff:
            diff_msg = "differ, but we don't know which is the good one"
        else:
            diff_msg = "look like the same images"
        vprint("They %s, ignoring..." % diff_msg)

        return

    if name in vmmap:
        vprint('An image with the same name is already in glance: ' + vmid)
        diff = False

        # Check MD5
        oldc = vmmap[name]['checksum']
        newc = new_md5
        if oldc != newc:
            vprint("But checksums differ, old: %s, new: %s" % (oldc, newc))
            diff = True

        # Check Version
        oldv = vmmap[name]['version']
        newv = mdata['version']
        if oldv != newv:
            vprint("But versions differ, old: %s, new: %s" % (oldv, newv))
            diff = True
            if oldv > newv:
                vprint("Versions are going backwards, that's not good.")
                vprint("Ignoring for now, fix the image on the market place.")
                return

        # This should not happen, as it should already have been caught by
        # earlier MD5 checking...
        if not diff:
            vprint("Identical images, that should not happen, please report"
                   " as a bug.")
            return

        if not glance.glance_rename(name, name + '_old'):
            vprint('Cannot rename old image, aborting update...')
            return

        vprint("Previous image renamed to: " + name + '_old')

    vprint("Uploading new image: " + name)
    glancing.main(['-v', '-s', new_md5, '-n', name, meta_file])
    glance.glance_update(name, '--property', 'version=' + mdata['version'])

def main(sys_argv=sys.argv[1:]):
    '''Download images specified in the given list & store them in glance
    '''
    args = do_argparse(sys_argv)
    vprint('Image list: ' + args.vmlist)
    if not args.vmlist or not os.path.exists(args.vmlist):
        print('Cannot access image list file: ' + args.vmlist)
        return False
    vmmap = get_glance_images()
    vmlist = get_vmlist(args.vmlist)
    for vmid in vmlist:
        vmid = vmid.strip()
        if vmid:
            handle_vm(vmid, vmmap)
    return True

if __name__ == '__main__':
    main()
