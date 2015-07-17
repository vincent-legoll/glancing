#! /usr/bin/env python

import sys
import unittest

from utils import get_local_path

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
