#! /usr/bin/env python

import os
import sys
import unittest

from tutils import get_local_path

# Setup PYTHONPATH for utils
sys.path.append(get_local_path('..', '..', 'src'))

import utils
import glance_manager

utils.set_verbose(True)

# Check we have a cloud ready to import images into...
_GLANCE_OK = False
with utils.devnull('stderr'):
    _GLANCE_OK = utils.run(['glance', 'image-list'])[0]

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlanceManagerTest(unittest.TestCase):

    def test_glance_manager_ok(self):
        glance_manager.get_meta_file = lambda x: get_local_path('..', 'stratuslab', 'cirros.xml')
        glance_manager.main(['-v', '-l', get_local_path('..', 'gm_list.txt')])
        
