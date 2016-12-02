#! /usr/bin/env python

import unittest

from tutils import local_pythonpath, get_local_path

# Setup project-local PYTHONPATH
local_pythonpath('..', '..', 'src')

import utils
import glance
import glance_manager

utils.set_verbose(True)

# Check we have a cloud ready to import images into...
_GLANCE_OK = False
with utils.devnull('stderr'):
    _GLANCE_OK = glance.glance_run('image-list') is not None

_OLDGMF = glance_manager.get_meta_file

class GlanceManagerBasicTest(unittest.TestCase):

    def test_glance_manager_nolist(self):
        ret = glance_manager.main([])
        self.assertFalse(ret)

    def test_glance_manager_badlistpath(self):
        ret = glance_manager.main(['-l', '/nonexistent'])
        self.assertFalse(ret)

    def test_glance_manager_nolist_verbose(self):
        ret = glance_manager.main(['-v'])
        self.assertFalse(ret)

    def test_glance_manager_gmf(self):
        with self.assertRaises(TypeError):
            glance_manager.get_meta_file(None, None)
        with self.assertRaises(TypeError):
            glance_manager.get_meta_file(None, '')
        with self.assertRaises(TypeError):
            glance_manager.get_meta_file(None, 'http://8.8.8.8')
        ret = glance_manager.get_meta_file('Buh-tYElvOEvst1HDyTq_6v-1si', 'http://8.8.8.8/')
        self.assertFalse(ret)
        ret = glance_manager.get_meta_file('Buh-tYElvOEvst1HDyTq_6v-1si', glance_manager._DEFAULT_SL_MP_URL)
        self.assertTrue(ret)

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlanceManagerTest(unittest.TestCase):

    def test_glance_manager_ok(self):
        cln = ['glance', '--os-image-api-version', '1', 'image-delete',
               'GLANCE_MANAGER_CIRROS_TESTING_IMAGE']
        with utils.cleanup(cln):
            locpath = get_local_path('..', 'gm_list.txt')
            ret = glance_manager.main(['-v', '-l', locpath])
            self.assertTrue(ret)

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlanceManagerTestMocked(unittest.TestCase):

    def setUp(self):
        gmf = lambda mpid, url: get_local_path('..', 'stratuslab', 'cirros.xml')
        glance_manager.get_meta_file = gmf

    def tearDown(self):
        glance_manager.get_meta_file = _OLDGMF

    def test_glance_manager_mocked_ok(self):
        cln = ['glance', '--os-image-api-version', '1', 'image-delete',
               'GLANCE_MANAGER_CIRROS_TESTING_IMAGE']
        with utils.cleanup(cln):
            locpath = get_local_path('..', 'gm_list.txt')
            ret = glance_manager.main(['-v', '-l', locpath])
            self.assertTrue(ret)

    def test_glance_manager_mocked_ok_double(self):
        cln = ['glance', '--os-image-api-version', '1', 'image-delete',
               'GLANCE_MANAGER_CIRROS_TESTING_IMAGE']
        with utils.cleanup(cln):
            locpath = get_local_path('..', 'gm_list.txt')
            ret = glance_manager.main(['-v', '-l', locpath, '-l', locpath])
            self.assertTrue(ret)

# TODO: test name with spaces characters (initial, update, etc...)
