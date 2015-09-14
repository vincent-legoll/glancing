#! /usr/bin/env python

from __future__ import print_function

import sys
import uuid
import argparse

import utils
import openstack_out

from utils import vprint, vprint_lines

_GLANCE_CMD = ['glance']

# Check glance availability early
def glance_ok():
    return glance_run(quiet=True) is not None

# Import VM image into glance
def glance_import(base, md5=None, name=None, diskformat=None):
    args = ['--container-format', 'bare', '--file', base]
    if diskformat is not None:
        args += ['--disk-format', diskformat]
    if name is not None:
        args += ['--name', name]
    if md5 is not None:
        args += ['--checksum', md5]
    err_msg = 'failed to import image into glance: %s from %s' % (name, base)
    out = glance_run('image-create', *args, err_msg=err_msg)
    return out is not None

def glance_exists(name):
    if type(name) not in (str, unicode):
        vprint('glance_exists(name=%s): name is not a string, but a %s' % (name, str(type(name))))
        raise TypeError
    return len(glance_ids([name])) > 0

def glance_run(glance_cmd=None, *args, **kwargs):
    cmd = list(_GLANCE_CMD)
    if glance_cmd is not None:
        cmd += [glance_cmd]
    cmd.extend(args)
    ok, retcode, out, err = utils.run(cmd, out=True, err=True)
    if not ok:
        if not (kwargs.get('quiet') == True):
            err_msg = kwargs.get('err_msg', 'failed to run "%s"' % glance_cmd)
            vprint(err_msg)
            if args:
                vprint('args: %s' % str(args))
            vprint_lines('stdout=' + out)
            vprint_lines('stderr=' + err)
        return None
    return out

def glance_ids(names=None):
    ret = set()
    # Single name ?
    if type(names) in (str, unicode):
        names = [names]
    il = glance_run('image-list')
    if il:
        h, b, _, _ = openstack_out.parse_block(il)
        for image_id, image_name, _, _, _, _ in b:
            # Filtering or not ?
            if (names is None or (utils.is_iter(names) and
                (image_name in names or image_id in names))):
                ret.add(image_id)
    return ret

def glance_delete_all(names, quiet=False):
    ret = False
    all_images_ids = glance_ids(names)
    if all_images_ids:
        ret = glance_delete_ids(all_images_ids, quiet=quiet)
    return ret

def glance_delete_ids(ids, quiet=False):
    ret = True
    for image_id in ids:
        ret &= glance_delete(image_id, quiet=quiet)
    return ret

def glance_delete(name, quiet=False):
    err_msg = 'failed to delete image from glance: ' + name
    out = glance_run('image-delete', name, err_msg=err_msg, quiet=quiet)
    return out is not None

def glance_download(name, fn_local):
    err_msg = 'failed to download image from glance: ' + name
    out = glance_run('image-download', '--file', fn_local, name, err_msg=err_msg)
    return out is not None

def glance_rename(vmid, name):
    err_msg = 'failed to rename image from glance: ' + name
    out = glance_run('image-update', '--name', name, vmid, err_msg=err_msg)
    return out is not None

# Handle CLI options
def do_argparse(sys_argv):
    parser = argparse.ArgumentParser(description='Manage glance VM images')

    # Global options
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display additional information')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--delete', dest='delete', metavar='NAME', nargs='+',
                       help='delete all images with the same name as '
                            'the specified VM')

    args = parser.parse_args(sys_argv)

    if args.verbose:
        utils.set_verbose(True)
        vprint('verbose mode')

    return args

def main(sys_argv=sys.argv):
    args = do_argparse(sys_argv)
    if args.delete:
        glance_delete_all(args.delete)
    return True

if __name__ == '__main__':
    main()
