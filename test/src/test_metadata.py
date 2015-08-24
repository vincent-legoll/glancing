#! /usr/bin/env python

import os
import sys
import unittest

from tutils import get_local_path

# Setup PYTHONPATH for metadata
sys.path.append(get_local_path('..', '..', 'src'))

from utils import devnull

import metadata

good_keys = set([
    'os',
    'bytes',
    'format',
    'os-arch',
    'location',
    'checksums',
    'os-version',
    'compression',
])

class TestMetaDataJson(unittest.TestCase):

    def metadata_test(self):
        fn = 'PIDt94ySjKEHKKvWrYijsZtclxU.json'
        jsonfile = get_local_path('..', 'stratuslab', fn)
        m = metadata.MetaStratusLabJson(jsonfile)
        md = m.get_metadata()
        self.assertEqual(set(md.keys()), good_keys)
        self.assertEqual(md['location'],
            'http://appliances.stratuslab.eu/images/base/'
            'CentOS-7-Server-x86_64/1.1/CentOS-7-Server-x86_64.dsk.gz')

class TestMetaDataCern(unittest.TestCase):

    def metadata_test(self):
        fn = 'hepix_signed_image_list' # image.list
        jsonfile = get_local_path('..', 'CERN', fn)
        m = metadata.MetaCern(jsonfile)
        md = m.get_metadata('623b0bc7-abc2-4961-8700-53e358772a96')
        self.assertEqual(set(md.keys()), good_keys)
        self.assertEqual(md['location'],
            'https://cernvm.cern.ch/releases/25/'
            'cernvm-batch-node-2.7.2-1-2-x86_64.hdd.gz')

class TestMetaDataXml(unittest.TestCase):

    def metadata_test(self):
        fn = 'KqU_1EZFVGCDEhX9Kos9ckOaNjB.xml'
        xmlfile = get_local_path('..', 'stratuslab', fn)
        m = metadata.MetaStratusLabXml(xmlfile)
        md = m.get_metadata()
        self.assertEqual(set(md.keys()), good_keys)
        self.assertEqual(md['location'],
            'http://www.apc.univ-paris7.fr/Downloads/comput/'
            'CentOS7.qcow2.gz')

class TestMetaDataJsonFixture(unittest.TestCase):

    fn = 'test.json'

    def setUp(self):
        if os.path.exists(self.fn):
            os.remove(self.fn)

    tearDown = setUp

    def metadata_test_not_dict(self):
        with open(self.fn, 'wb') as jsonf:
            jsonf.write('""\n')
        with devnull('stderr'):
            with self.assertRaises(ValueError):
                m = metadata.MetaStratusLabJson(self.fn)
