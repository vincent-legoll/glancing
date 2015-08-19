#! /usr/bin/env python

import os
import sys
import unittest

from tutils import get_local_path

# Setup PYTHONPATH for metadata
sys.path.append(get_local_path('..', '..', 'src'))

from utils import devnull

import metadata

class TestMetaData(unittest.TestCase):

    def metadata_test(self):
        fn = 'PIDt94ySjKEHKKvWrYijsZtclxU.json'
        jsonfile = get_local_path('..', 'stratuslab', fn)
        m = metadata.MetaStratusLab(jsonfile)
        md = m.get_metadata()
        self.assertIn('url', md)
        self.assertEqual(md['url'],
            'http://appliances.stratuslab.eu/images/base/'
            'CentOS-7-Server-x86_64/1.1/CentOS-7-Server-x86_64.dsk.gz')

class TestMetaDataFixture(unittest.TestCase):

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
                m = metadata.MetaStratusLab(self.fn)
