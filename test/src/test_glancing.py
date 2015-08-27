#! /usr/bin/env python

import os
import sys
import unittest

from tutils import get_local_path

# Setup PYTHONPATH for glancing, utils
sys.path.append(get_local_path('..', '..', 'src'))

from utils import devnull, environ, test_name, run, cleanup

import glancing

# Check we have a cloud ready to import images into...
_GLANCE_OK = False
with devnull('stderr'):
    _GLANCE_OK = run(['glance', 'image-list'])[0]

# Avoid heavy image download tests
_HEAVY_TESTS = False # < 500 MB images, ~2 min -> ~6 min...
_HUGE_TESTS = False # 1 x 5 GB image

class GlancingMiscTest(unittest.TestCase):

    def test_glancing_main_glance_availabilityFail(self):
        with environ('PATH'):
            self.assertFalse(glancing.main([os.devnull]))

    @unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
    def test_glancing_main_glance_availabilityOK(self):
        with cleanup(['glance', 'image-delete', 'null']):
            self.assertTrue(glancing.main([os.devnull]))

    def test_glancing_empty_cli_param(self):
        self.assertFalse(glancing.main(['']))
        self.assertFalse(glancing.main(['-d', '']))

class GlancingImageDryRunNotExistentTest(unittest.TestCase):

    def test_glancing_image_notexistent(self):
        self.assertFalse(glancing.main(['-d', '/notexistent.txt']))

    def test_glancing_image_notexistent_sum(self):
        self.assertFalse(glancing.main(['-d', '/notexistent.txt',
            '-s', '0' * 32]))

class GlancingImageDryRunDevnullTest(unittest.TestCase):

    _DEVNULL_MD5 = 'd41d8cd98f00b204e9800998ecf8427e'

    def test_glancing_image_devnull(self):
        self.assertTrue(glancing.main(['-d', os.devnull]))

    def test_glancing_image_notenough_param(self):
        with devnull('stderr'):
            with self.assertRaises(SystemExit):
                glancing.main(['-d', os.devnull, '-s'])

    def test_glancing_image_devnull_sum_bad(self):
        sums = ['### BAD CHECKSUM ###', '0' * 32, self._DEVNULL_MD5 +
            ':' + '0' * 32]
        for asum in sums:
            self.assertFalse(glancing.main(['-d', os.devnull, '-s', asum]))

    def test_glancing_image_devnull_sum_empty(self):
        self.assertTrue(glancing.main(['-d', os.devnull, '-s', '']))

    def test_glancing_image_devnull_sum(self):
        self.assertTrue(glancing.main(['-d', os.devnull, '-s',
            self._DEVNULL_MD5]))

    def test_glancing_image_devnull_sum_verbose(self):
        self.assertTrue(glancing.main(['-dv', os.devnull, '-s',
            self._DEVNULL_MD5]))

class TestGlancingImageTtylinuxBase(unittest.TestCase):

    _TTYLINUX_FILE = get_local_path('..', 'images', 'ttylinux-16.1-x86_64.img')
    _TTYLINUX_MD5 = '3d1b4804dcf2a613f0ed4a91b9ed2b98'

class GlancingImageDryRunTtylinuxTest(TestGlancingImageTtylinuxBase):

    def test_glancing_image_ttylinux(self):

        md5 = self._TTYLINUX_MD5
        sha1 = '1b5229d5dad92bc7952553be01608af2180eafbe'
        sha512 = ('79556bc3a25e4555a6cd71afba8eae80eb6d5f23f16a84e6' +
                  '017a54469034cf77ee7bcd74ac285c6ec42c25547b6963c1' +
                  'e7232d4fcca388a326f0ec3e7afb838e')

        self.assertTrue(glancing.main(['-d', self._TTYLINUX_FILE]))

        checksums_true = ['', ':', ':::::', sha512, sha1 + ':' + md5,
            md5 + ':', ':' + md5]

        for chks in checksums_true:
            self.assertTrue(glancing.main(['-d',
                self._TTYLINUX_FILE, '-s', chks]), chks)

        checksums_false = ['a' + md5, 'a' + md5 + ':' + md5, md5[:12] +
            '0' + md5[13:], md5 + ':' + md5[:12] + '0' + md5[13:]]

        for chks in checksums_false:
            self.assertFalse(glancing.main(['-d',
                self._TTYLINUX_FILE, '-s', chks]), chks)

class GlancingImageDryRunCoreosTest(unittest.TestCase):

    def test_glancing_image_coreos(self):
        fn = 'coreos_production_qemu_image.img'
        imgfile = get_local_path('..', 'images', fn)
        md5 = '1b0d8f7e4ff1128e3527ad6e15ae0855'
        self.assertTrue(glancing.main(['-d', imgfile, '-s',
            md5 + ':' + md5]))

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlancingImageTest(TestGlancingImageTtylinuxBase):

    def test_glancing_image_import_noname(self):
        name, ext = os.path.splitext(os.path.basename(self._TTYLINUX_FILE))
        with cleanup(['glance', 'image-delete', name]):
            self.assertTrue(glancing.main(['-f',
                self._TTYLINUX_FILE, '-s', self._TTYLINUX_MD5]))

    def test_glancing_image_import_name(self):
        with cleanup(['glance', 'image-delete', test_name()]):
            self.assertTrue(glancing.main(['-n', test_name(),
                self._TTYLINUX_FILE, '-s', self._TTYLINUX_MD5]))

    def test_glancing_image_import_name_bad_md5(self):
        with cleanup(['glance', 'image-delete', test_name()]):
            self.assertFalse(glancing.main(['-n', test_name(),
                self._TTYLINUX_FILE, '-s', '0' * 32]))

    def test_glancing_image_import_name_force(self):
        with cleanup(['glance', 'image-delete', test_name()]):
            self.assertTrue(glancing.main(['-f', '-n', test_name(),
                self._TTYLINUX_FILE, '-s', '0' * 32]))

class GlancingMetadataTest(unittest.TestCase):

    @unittest.skipUnless(_HEAVY_TESTS, "image too big")
    def test_glancing_metadata_heavies(self):
        market_ids = (
            # 98 MB, size & checksum mismatch: 4 B -> 98 MB
            ('JcqGhHxmTRAEpHMmRF-xhSTM3TO', False, False),
            # 102 MB, does not exists any more on SL marketplace
            ('BtSKdXa2SvHlSVTvgFgivIYDq--', True, False),
            # 463 MB
            ('KqU_1EZFVGCDEhX9Kos9ckOaNjB', True, True),
            # Size & checksum mismatch: 375 MB -> 492 MB
            ('ME4iRTemHRwhABKV5AgrkQfDerA', False, False),
        )
        for market_id, status_json, status_market in market_ids:
            mdfile = get_local_path('..', 'stratuslab', market_id +
                '.json')
            self.assertEqual(status_json, glancing.main(['-d',
                mdfile]), mdfile)
            self.assertEqual(status_market, glancing.main(['-d',
                market_id]), market_id)

    @unittest.skipUnless(_HEAVY_TESTS, "image too big")
    @unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
    def test_glancing_metadata_bad_but_force(self):
        # Size & checksum mismatch: 375 MB -> 492 MB
        market_id = 'ME4iRTemHRwhABKV5AgrkQfDerA'
        mdfile = get_local_path('..', 'stratuslab', market_id + '.json')
        with cleanup(['glance', 'image-delete', test_name()]):
            self.assertTrue(glancing.main(['-f', '-n', test_name(),
                mdfile]))
        with cleanup(['glance', 'image-delete', test_name()]):
            self.assertTrue(glancing.main(['-f', '-n', test_name(),
                market_id]))

    @unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
    def test_glancing_metadata_cirros_import(self):
        # 12 MB
        mdfile = get_local_path('..', 'stratuslab', 'cirros.json')
        with devnull('stderr'):
            with cleanup(['glance', 'image-delete', test_name()]):
                self.assertTrue(glancing.main(['-v', '-n', test_name(),
                    mdfile, '-k']))

    @unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
    def test_glancing_metadata_cirros_import_no_cksum(self):
        # 12 MB
        mdfile = get_local_path('..', 'stratuslab', 'cirros_no_cksum.json')
        with devnull('stderr'):
            with cleanup(['glance', 'image-delete', test_name()]):
                self.assertTrue(glancing.main(['-v', '-n', test_name(),
                    mdfile, '-k']))

    @unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
    def test_glancing_metadata_cirros_import_bad_size(self):
        # 12 MB
        mdfile = get_local_path('..', 'stratuslab', 'cirros_bad_size.json')
        with devnull('stderr'):
            with cleanup(['glance', 'image-delete', test_name()]):
                self.assertFalse(glancing.main(['-v', '-n', test_name(),
                    mdfile]))
            with cleanup(['glance', 'image-delete', test_name()]):
                self.assertTrue(glancing.main(['-f', '-n', test_name(),
                    mdfile]))

    @unittest.skipUnless(_HUGE_TESTS, "image too big: 5.0 GB")
    def test_glancing_metadata_big(self):
        market_id = 'PIDt94ySjKEHKKvWrYijsZtclxU'
        mdfile = get_local_path('..', 'stratuslab', market_id + '.json')
        self.assertFalse(glancing.main(['-d', mdfile]))
        self.assertFalse(glancing.main(['-d', market_id]))

class GlancingUrlDryRunTest(unittest.TestCase):

    def test_glancing_url_notenough_param(self):
        with devnull('stderr'):
            with self.assertRaises(SystemExit):
                url = 'http://nulle.part.fr/nonexistent_file.txt'
                glancing.main(['-d', url, '-s'])

    def test_glancing_url_notexistent(self):
        url = 'http://nulle.part.fr/nonexistent_file.txt'
        self.assertFalse(glancing.main(['-d', url]))

# FIXME: get a new image list
@unittest.skip("Obsolete CERN VM list file")
class GlancingCernTest(unittest.TestCase):

    def test_glancing_cern(self):
        cern_id = '623b0bc7-abc2-4961-8700-53e358772a96'
        jsonfile = get_local_path('..', 'CERN', 'hepix_signed_image_list')
        self.assertTrue(glancing.main(['-dvk', '-c', jsonfile, cern_id]))

class BaseGlancingUrl(unittest.TestCase):

    _CIRROS_URL = 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-i386-disk.img'
    _CIRROS_MD5 = '79b4436412283bb63c2cba4ac796bcd9'

class GlancingUrlDryRunCirrosTest(BaseGlancingUrl):

    def test_glancing_url(self):
        self.assertTrue(glancing.main(['-d', self._CIRROS_URL]))

    def test_glancing_url_md5(self):
        self.assertTrue(glancing.main(['-d', self._CIRROS_URL,
                                       '-s', self._CIRROS_MD5]))

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlancingUrlImportTest(BaseGlancingUrl):

    def test_glancing_url_import_no_name(self):
        name, ext = os.path.splitext(os.path.basename(self._CIRROS_URL))
        with cleanup(['glance', 'image-delete', name]):
            self.assertTrue(glancing.main([self._CIRROS_URL]))

    def test_glancing_url_import_bad_md5(self):
        with cleanup(['glance', 'image-delete', test_name()]):
            self.assertFalse(glancing.main(['-n', test_name(),
                self._CIRROS_URL, '-s', '0' * 32]))

    def test_glancing_url_import_bad_md5_but_force(self):
        with cleanup(['glance', 'image-delete', test_name()]):
            self.assertTrue(glancing.main(['-f', '-n', test_name(),
                self._CIRROS_URL, '-s', '0' * 32]))

    def test_glancing_url_import_no_md5(self):
        with cleanup(['glance', 'image-delete', test_name()]):
            self.assertTrue(glancing.main(['-n', test_name(),
                self._CIRROS_URL]))

    def test_glancing_url_import_good_md5(self):
        with cleanup(['glance', 'image-delete', test_name()]):
            self.assertTrue(glancing.main(['-n', test_name(),
                self._CIRROS_URL, '-s', self._CIRROS_MD5]))

