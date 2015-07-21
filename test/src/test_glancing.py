#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import unittest

from utils import get_local_path, devnull, environ

# Setup PYTHONPATH for glancing
sys.path.append(get_local_path('..', '..', 'src'))

import glancing

# Check we have a cloud ready to import images into...
_GLANCE_OK = False
with devnull('stderr'):
    _GLANCE_OK = glancing.check_glance_availability(['glance', 'image-list'])

class TestGlancingMisc(unittest.TestCase):

    def glancing_test_check_glance_availability(self):
        self.assertFalse(glancing.check_glance_availability(['g l a n c e']))

    def glancing_test_main_glance_availability(self):
        with environ('PATH', None):
            self.assertFalse(glancing.main(['image', '/dev/null', '-s', '### NOCHECKSUM ###']))

class TestGlancingImage(unittest.TestCase):

    def glancing_test_image_no_param(self):
        with devnull('stderr'):
            with self.assertRaises(SystemExit):
                glancing.main(['-d', 'image'])

    def glancing_test_image_notenough_param(self):
        with devnull('stderr'):
            with self.assertRaises(SystemExit):
                glancing.main(['-d', 'image', '/dev/null', '-s'])

    def glancing_test_image_devnull(self):
        self.assertTrue(glancing.main(['-d', 'image', '/dev/null', '-s', 'd41d8cd98f00b204e9800998ecf8427e']))

    def glancing_test_image_notexistent(self):
        self.assertFalse(glancing.main(['-d', 'image', '/notexistent.txt']))

    def glancing_test_image_notexistent_sum(self):
        self.assertFalse(glancing.main(['-d', 'image', '/notexistent.txt', '-s', 'd41d8cd98f00b204e9800998ecf8427e']))

    def glancing_test_image_one(self):

        fn = 'ttylinux-16.1-x86_64.img'
        imgfile = get_local_path('..', 'images', fn)
        md5 = '3d1b4804dcf2a613f0ed4a91b9ed2b98'
        sha1 = '1b5229d5dad92bc7952553be01608af2180eafbe'
        sha512 = '79556bc3a25e4555a6cd71afba8eae80eb6d5f23f16a84e6017a54469034cf77ee7bcd74ac285c6ec42c25547b6963c1e7232d4fcca388a326f0ec3e7afb838e'

        self.assertTrue(glancing.main(['-d', 'image', imgfile]))
        self.assertTrue(glancing.main(['-d', 'image', imgfile, '-s', '']))
        self.assertTrue(glancing.main(['-d', 'image', imgfile, '-s', ':']))
        self.assertTrue(glancing.main(['-d', 'image', imgfile, '-s', ':::::']))
        self.assertTrue(glancing.main(['-d', 'image', imgfile, '-s', sha512]))
        self.assertTrue(glancing.main(['-d', 'image', imgfile, '-s', sha1 + ':' + md5]))
        self.assertTrue(glancing.main(['-d', 'image', imgfile, '-s', md5 + ':']))
        self.assertTrue(glancing.main(['-d', 'image', imgfile, '-s', ':' + md5]))
        self.assertFalse(glancing.main(['-d', 'image', imgfile, '-s', 'a' + md5]))
        self.assertFalse(glancing.main(['-d', 'image', imgfile, '-s', 'a' + md5 + ':' + md5]))
        self.assertFalse(glancing.main(['-d', 'image', imgfile, '-s', md5[:12] + '0' + md5[13:]]))
        self.assertFalse(glancing.main(['-d', 'image', imgfile, '-s', md5 + ':' + md5[:12] + '0' + md5[13:]]))

    def glancing_test_image_two(self):
        fn = 'coreos_production_qemu_image.img'
        imgfile = get_local_path('..', 'images', fn)
        md5 = 'c9bc62eabccf1e4566cf216083fa3510'
        self.assertTrue(glancing.main(['-d', 'image', imgfile, '-s', md5 + ':' + md5]))

class TestGlancingMetadata(unittest.TestCase):

    def glancing_test_metadata_no_param(self):
        with devnull('stderr'):
            with self.assertRaises(SystemExit):
                glancing.main(['-d', 'json'])

    def glancing_test_metadata_not_json(self):
        with devnull('stderr'):
            with self.assertRaises(ValueError):
                glancing.main(['-d', 'json', '/dev/null'])

    def glancing_test_metadata_one(self):
        # 98 MB
        fn = 'JcqGhHxmTRAEpHMmRF-xhSTM3TO.json'
        mdfile = get_local_path('..', 'stratuslab', fn)
        self.assertFalse(glancing.main(['-d', 'json', mdfile]))

    def glancing_test_metadata_two(self):
        # 102 MB
        fn = 'BtSKdXa2SvHlSVTvgFgivIYDq--.json'
        mdfile = get_local_path('..', 'stratuslab', fn)
        self.assertTrue(glancing.main(['-d', 'json', mdfile]))

    def glancing_test_metadata_three(self):
        # Size mismatch: 375 MB -> 492 MB
        fn = 'ME4iRTemHRwhABKV5AgrkQfDerA.json'
        mdfile = get_local_path('..', 'stratuslab', fn)
        self.assertFalse(glancing.main(['-d', 'json', mdfile]))

    @unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
    def glancing_test_metadata_cirros_import(self):
        # 12 MB
        fn = 'cirros.json'
        mdfile = get_local_path('..', 'stratuslab', fn)
        with devnull('stderr'):
            self.assertTrue(glancing.main(['-n', 'test_import_cirros', 'json', mdfile]))
        # Cleanup
        glancing.check_glance_availability(['glance', 'image-delete', 'test_import_cirros'])

    @unittest.skip("5GB image, too big")
    def glancing_test_metadata_big(self):
        fn = 'PIDt94ySjKEHKKvWrYijsZtclxU.json'
        mdfile = get_local_path('..', 'stratuslab', fn)
        self.assertFalse(glancing.main(['-d', 'json', mdfile]))

class TestGlancingUrl(unittest.TestCase):

    def glancing_test_url_no_param(self):
        with devnull('stderr'):
            with self.assertRaises(SystemExit):
                glancing.main(['-d', 'url'])

    def glancing_test_url_notenough_param(self):
        with devnull('stderr'):
            with self.assertRaises(SystemExit):
                url = 'http://nulle.part.fr/nonexistent_file.txt'
                glancing.main(['-d', 'url', url, '-s'])

    def glancing_test_url_notexistent(self):
        url = 'http://nulle.part.fr/nonexistent_file.txt'
        self.assertFalse(glancing.main(['-d', 'url', url]))

    def glancing_test_url(self):
        url = 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-i386-disk.img'
        self.assertTrue(glancing.main(['-d', 'url', url]))
