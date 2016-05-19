#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import argparse

import utils
import openstack_out

from utils import vprint, vprint_lines

_GLANCE_CMD = ['glance']

# Check glance availability early
def glance_ok():
    return glance_run(quiet=True) is not None

# Import VM image into glance
def glance_import_id(base, md5=None, name=None, diskformat=None):
    g_args = None
    args = ['--container-format', 'bare', '--file', base]
    if diskformat is not None:
        args += ['--disk-format', diskformat]
    if name is not None:
        args += ['--name', name]
    if md5 is not None:
        args += ['--checksum', md5]
        # Passing in the checksum has been deprecated in API v2.x
        g_args = ['--os-image-api-version', '1']
    err_msg = 'failed to import image into glance: %s from %s' % (name, base)
    out = glance_run('image-create', g_args, *args, err_msg=err_msg)
    if out:
        _, block, _, _ = openstack_out.parse_block(out)
        for property_name, value in block:
            if property_name == 'id':
                return value
    return False

def glance_import(base, md5=None, name=None, diskformat=None):
    return not not glance_import_id(base, md5, name, diskformat)

def glance_exists(name):
    if type(name) not in (str, unicode):
        vprint('glance_exists(name=%s): name is not a string, but a %s' % (name, str(type(name))))
        raise TypeError
    return len(glance_ids([name])) > 0

def glance_run(glance_cmd=None, g_args=None, *args, **kwargs):
    cmd = list(_GLANCE_CMD)
    if g_args is not None:
        cmd.extend(g_args)
    # Handle site-specific parameters (for example: "--insecure")
    os_params = os.environ.get('OS_PARAMS', None)
    if os_params:
        cmd[1:1] = os_params.split()
    if glance_cmd is not None:
        cmd += [glance_cmd]
    cmd.extend(args)
    status, _, out, err = utils.run(cmd, out=True, err=True)
    if not status:
        if not kwargs.get('quiet') is True:
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
    imglist = glance_run('image-list')
    if imglist:
        _, block, _, _ = openstack_out.parse_block(imglist)
        for image_id, image_name in block:
            # Filtering or not ?
            if (names is None or (utils.is_iter(names) and
                    (image_name in names or image_id in names))):
                ret.add(image_id)
    return ret

def glance_id(name):
    # FIXME: We don't handle images with uuid as name
    if utils.is_uuid(name):
        return name
    name = glance_ids(name)
    if name and len(name) > 0:
        return list(name)[0]
    # Non-existent image
    return None

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

def glance_show(name, quiet=False):
    imgid = glance_id(name)
    if imgid is None:
        return False
    err_msg = 'failed to get infos from glance for image: ' + str(imgid)
    out = glance_run('image-show', None, imgid, err_msg=err_msg, quiet=quiet)
    return out

def glance_delete(name, quiet=False):
    imgid = glance_id(name)
    if imgid is None:
        return False
    err_msg = 'failed to delete image from glance: ' + str(imgid)
    out = glance_run('image-delete', None, imgid, err_msg=err_msg, quiet=quiet)
    return out is not None

def glance_download(name, fn_local):
    imgid = glance_id(name)
    if imgid is None:
        return False
    err_msg = 'failed to download image from glance: ' + str(imgid)
    out = glance_run('image-download', None, '--file', fn_local, imgid, err_msg=err_msg)
    return out is not None

def glance_rename(vmid, name):
    return glance_update(vmid, '--name', name)

def glance_update(vmid, *args):
    imgid = glance_id(vmid)
    if imgid is None:
        return False
    err_msg = 'failed to update image from glance: ' + str(imgid)
    args = list(args)
    args.append(imgid)
    out = glance_run('image-update', None, *args, err_msg=err_msg)
    return out is not None

# Handle CLI options
def do_argparse(sys_argv):
    parser = argparse.ArgumentParser(description='Manage glance VM images')

    # Global options
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display additional information')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--delete', dest='delete', metavar='NAME',
                       nargs='+', help='delete all images with the same '
                            'name as the specified VM')

    args = parser.parse_args(sys_argv)

    if args.verbose:
        utils.set_verbose(True)
        vprint('verbose mode')

    return args

def main(sys_argv=sys.argv[1:]):
    args = do_argparse(sys_argv)
    if args.delete:
        glance_delete_all(args.delete)
    return True

if __name__ == '__main__':
    main()
