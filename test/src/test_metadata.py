#! /usr/bin/env python

import os
import sys
import unittest

from tutils import local_pythonpath, get_local_path

# Setup project-local PYTHONPATH
local_pythonpath('..', '..', 'src')

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

class MetaDataJsonTest(unittest.TestCase):

    def test_metadata_json(self):
        fn = 'PIDt94ySjKEHKKvWrYijsZtclxU.json'
        jsonfile = get_local_path('..', 'stratuslab', fn)
        m = metadata.MetaStratusLabJson(jsonfile)
        md = m.get_metadata()
        self.assertEqual(set(md.keys()), good_keys)
        self.assertEqual(md['location'],
            'http://appliances.stratuslab.eu/images/base/'
            'CentOS-7-Server-x86_64/1.1/CentOS-7-Server-x86_64.dsk.gz')

    def test_metadata_json_bad(self):
        with devnull('stderr'):
            with self.assertRaises(ValueError):
                metadata.MetaStratusLabJson(os.devnull)

class MetaDataCernTest(unittest.TestCase):

    def test_metadata_cern(self):
        fn = 'test_image_list'
        jsonfile = get_local_path('..', 'CERN', fn)
        m = metadata.MetaCern(jsonfile, 'deadbabe-f00d-beef-cafe-b1ab1ab1a666')
        md = m.get_metadata()
        self.assertEqual(set(md.keys()), good_keys)
        self.assertEqual(md['location'],
            'http://download.cirros-cloud.net/0.3.4/'
            'cirros-0.3.4-i386-disk.img')

class MetaDataXmlTest(unittest.TestCase):

    def test_metadata_xml(self):
        fn = 'KqU_1EZFVGCDEhX9Kos9ckOaNjB.xml'
        xmlfile = get_local_path('..', 'stratuslab', 'download', fn)
        m = metadata.MetaStratusLabXml(xmlfile)
        md = m.get_metadata()
        self.assertEqual(set(md.keys()), good_keys)
        self.assertEqual(md['location'],
            'http://www.apc.univ-paris7.fr/Downloads/comput/'
            'CentOS7.qcow2.gz')

    def test_metadata_xml_bad(self):
        m = metadata.MetaStratusLabXml(os.devnull)
        self.assertIsNone(m.get_metadata())

class MetaDataJsonFixtureTest(unittest.TestCase):

    fn = 'test.json'

    def setUp(self):
        if os.path.exists(self.fn):
            os.remove(self.fn)

    tearDown = setUp

    def test_metadata_json_fixture_not_dict(self):
        with open(self.fn, 'wb') as jsonf:
            jsonf.write('""\n')
        with devnull('stderr'):
            with self.assertRaises(ValueError):
                m = metadata.MetaStratusLabJson(self.fn)
