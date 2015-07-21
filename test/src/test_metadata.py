#! /usr/bin/env python

import os
import sys
import unittest

from utils import get_local_path, devnull

# Setup PYTHONPATH for metadata
sys.path.append(get_local_path('..', '..', 'src'))

import metadata

class TestMetaData(unittest.TestCase):

    def metadata_test(self):
        fn = 'PIDt94ySjKEHKKvWrYijsZtclxU.json'
        jsonfile = get_local_path('..', 'stratuslab', fn)
        m = metadata.MetaStratusLab(jsonfile)
        md = m.get_metadata()
        self.assertIn('url', md)
        self.assertEqual(md['url'],
                         'http://appliances.stratuslab.eu/images/base/CentOS-7-Server-x86_64/1.1/CentOS-7-Server-x86_64.dsk.gz')

    def metadata_test_not_dict(self):
        fn = 'test.json'
        if os.path.exists(fn):
            os.remove(fn)
        with open(fn, 'wb') as jsonf:
            jsonf.write('""\n')
        with devnull('stderr'):
            with self.assertRaises(ValueError):
                m = metadata.MetaStratusLab(fn)
        if os.path.exists(fn):
            os.remove(fn)
