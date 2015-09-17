#! /usr/bin/env python

import os
import sys
import unittest

from tutils import local_pythonpath, get_local_path

# Setup project-local PYTHONPATH
local_pythonpath('..', '..', 'src')

import utils
import glance_manager

utils.set_verbose(True)

# Check we have a cloud ready to import images into...
_GLANCE_OK = False
with utils.devnull('stderr'):
    _GLANCE_OK = utils.run(['glance', 'image-list'])[0]

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlanceManagerTest(unittest.TestCase):

    def test_glance_manager_mocked_ok(self):
        gmf = lambda x: get_local_path('..', 'stratuslab', 'cirros.xml')
        glance_manager.get_meta_file = gmf
        self.assertTrue(glance_manager.main(['-v', '-l',
            get_local_path('..', 'gm_list.txt')]))

    def test_glance_manager_ok(self):
        self.assertTrue(glance_manager.main(['-v', '-l',
            get_local_path('..', 'gm_list.txt')]))
