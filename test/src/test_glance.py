#! /usr/bin/env python

import os
import unittest

from tutils import local_pythonpath

# Setup PYTHONPATH for utils
local_pythonpath('..', '..', 'src')

import glance
import utils

# Always verbose messages during tests
utils.set_verbose(True)

# Check we have a cloud ready to import images into...
_GLANCE_OK = False
with utils.devnull('stderr'):
    _GLANCE_OK = utils.run(['glance', 'image-list'])[0]

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlanceTest(unittest.TestCase):

    def test_glance_ok(self):
        self.assertTrue(glance.glance_ok())
        with utils.devnull('stderr'):
            with utils.environ('PATH', 'not_the_one'):
                self.assertFalse(glance.glance_ok())

    def test_glance_exists_raise(self):
        with self.assertRaises(TypeError):
            glance.glance_exists(None)
        with self.assertRaises(TypeError):
            glance.glance_exists(True)
        with self.assertRaises(TypeError):
            glance.glance_exists(False)
        with self.assertRaises(TypeError):
            glance.glance_exists([])

    def test_glance_exists_false(self):
        self.assertFalse(glance.glance_exists(''))
        self.assertFalse(glance.glance_exists('Nonexistent'))
        self.assertFalse(glance.glance_exists(u''))
        self.assertFalse(glance.glance_exists(u'Nonexistent'))

    def test_glance_ids_unfiltered(self):
        l1 = glance.glance_ids(None)
        self.assertTrue(set() <= l1)
        l2 = glance.glance_ids()
        self.assertTrue(set() <= l2)
        self.assertEqual(l1, l2)

    def test_glance_ids_single(self):
        self.assertEqual(set(), glance.glance_ids(True))
        self.assertEqual(set(), glance.glance_ids(False))
        self.assertEqual(set(), glance.glance_ids(''))
        self.assertEqual(set(), glance.glance_ids(u''))
        self.assertEqual(set(), glance.glance_ids([]))

    def test_glance_ids_list_single(self):
        self.assertEqual(set(), glance.glance_ids([None]))
        self.assertEqual(set(), glance.glance_ids([True]))
        self.assertEqual(set(), glance.glance_ids([False]))
        self.assertEqual(set(), glance.glance_ids(['']))
        self.assertEqual(set(), glance.glance_ids([u'']))
        self.assertEqual(set(), glance.glance_ids([[]]))

    def test_glance_ids_list(self):
        self.assertEqual(set(), glance.glance_ids([None, True, False]))
        self.assertEqual(set(), glance.glance_ids(['', u'']))

class TestGlanceNotOkGlanceIDS(unittest.TestCase):

    def test_glance_ids_uuid(self):
        glance.glance_delete_all(utils.test_name(), quiet=True)
        self.assertTrue(glance.glance_import(os.devnull,
                name=utils.test_name(), diskformat='raw'))
        img_uuids_name = list(glance.glance_ids(utils.test_name()))
        self.assertEqual(len(img_uuids_name), 1)
        img_uuid = img_uuids_name[0]
        img_uuids_uuid = list(glance.glance_ids(img_uuid))
        self.assertEqual(img_uuids_uuid, img_uuids_name)
        glance.glance_delete_all(utils.test_name(), quiet=True)

class TestGlanceNotOk(unittest.TestCase):

    def test_glance_diskformat(self):
        glance.glance_delete_all(utils.test_name(), quiet=True)
        self.assertFalse(glance.glance_import(os.devnull,
                name=utils.test_name(), diskformat='notgood'))
        self.assertFalse(glance.glance_import(os.devnull,
                name=utils.test_name()))
        glance.glance_delete_all(utils.test_name(), quiet=True)

    def test_glance_imglist(self):
        self.assertTrue(glance.glance_run('image-list'))
        with utils.environ('OS_PASSWORD', 'not_the_one'):
            self.assertFalse(glance.glance_run('image-list'))

    def test_glance_ids(self):
        self.assertEqual(set(), glance.glance_ids('XXX'))
        with utils.environ('OS_PASSWORD', 'not_the_one'):
            self.assertEqual(set(), glance.glance_ids('XXX'))

class TestGlanceFixture(unittest.TestCase):

    _IMG_NAME = 'test-glance-img'

    def setUp(self):
        glance.glance_delete_all(self._IMG_NAME, quiet=True)

    tearDown = setUp

    def common_start(self, name=None, filename=os.devnull):
        self.assertFalse(glance.glance_exists(self._IMG_NAME))
        self.assertTrue(glance.glance_import(filename, name=name, diskformat='raw'))
        self.assertTrue(glance.glance_exists(self._IMG_NAME))

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlanceNoNameTest(TestGlanceFixture):

    _IMG_NAME = ''

    def test_glance_main_noname(self):
        self.common_start()
        self.assertTrue(glance.main(['-d', self._IMG_NAME]))
        self.assertFalse(glance.glance_exists(self._IMG_NAME))

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlanceNoNameTestUnicode(TestGlanceFixture):

    _IMG_NAME = u''

    def test_glance_main_noname(self):
        self.common_start()
        self.assertTrue(glance.main(['-d', self._IMG_NAME]))
        self.assertFalse(glance.glance_exists(self._IMG_NAME))

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlanceMainTest(TestGlanceFixture):

    def test_glance_main_ok_nodelete(self):
        self.common_start(self._IMG_NAME)
        self.assertTrue(glance.main(['-v']))
        self.assertTrue(glance.glance_exists(self._IMG_NAME))

    def test_glance_main_ok(self):
        self.common_start(self._IMG_NAME)
        self.assertTrue(glance.main(['-d', self._IMG_NAME]))
        self.assertFalse(glance.glance_exists(self._IMG_NAME))

    def test_glance_main_ok_verbose(self):
        self.common_start(self._IMG_NAME)
        self.assertTrue(glance.main(['-v', '-d', self._IMG_NAME]))
        self.assertFalse(glance.glance_exists(self._IMG_NAME))

    def test_glance_main_fail_wrong_param_delete(self):
        self.common_start(self._IMG_NAME)
        with self.assertRaises(SystemExit):
            with utils.devnull('stderr'):
                glance.main(['-d'])
        self.assertTrue(glance.glance_exists(self._IMG_NAME))

    def test_glance_main_fail_wrong_param_name(self):
        self.common_start(self._IMG_NAME)
        with self.assertRaises(SystemExit):
            with utils.devnull('stderr'):
                glance.main([self._IMG_NAME])
        self.assertTrue(glance.glance_exists(self._IMG_NAME))

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlanceDeleteTest(TestGlanceFixture):

    def test_glance_delete_all(self):
        self.common_start(self._IMG_NAME)
        self.assertTrue(glance.glance_import(os.devnull, name=self._IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_import(os.devnull, name=self._IMG_NAME, diskformat='raw'))
        self.assertTrue(glance.glance_exists(self._IMG_NAME))
        self.assertTrue(glance.glance_delete_all(self._IMG_NAME))
        self.assertFalse(glance.glance_exists(self._IMG_NAME))

    def test_glance_delete_ok(self):
        self.common_start(self._IMG_NAME)
        self.assertTrue(glance.glance_delete(self._IMG_NAME))
        self.assertFalse(glance.glance_exists(self._IMG_NAME))

    def test_glance_delete_ok_quiet(self):
        self.common_start(self._IMG_NAME)
        self.assertTrue(glance.glance_delete(self._IMG_NAME, quiet=True))
        self.assertFalse(glance.glance_exists(self._IMG_NAME))

    def test_glance_delete_fail(self):
        self.common_start(self._IMG_NAME)
        self.assertTrue(glance.glance_delete(self._IMG_NAME))
        self.assertFalse(glance.glance_exists(self._IMG_NAME))

        self.assertFalse(glance.glance_delete(self._IMG_NAME))

    def test_glance_delete_fail_quiet(self):
        self.common_start(self._IMG_NAME)
        self.assertTrue(glance.glance_delete(self._IMG_NAME, quiet=True))
        self.assertFalse(glance.glance_exists(self._IMG_NAME))

        self.assertFalse(glance.glance_delete(self._IMG_NAME, quiet=True))

@unittest.skipUnless(_GLANCE_OK, "glance not properly configured")
class GlanceMiscTest(TestGlanceFixture):

    def test_glance_exists_import(self):
        self.common_start(self._IMG_NAME)

    def test_glance_rename_and_back(self):
        old = '_rename_test'
        self.common_start(self._IMG_NAME)
        self.assertFalse(glance.glance_exists(self._IMG_NAME + old))
        self.assertTrue(glance.glance_rename(self._IMG_NAME, self._IMG_NAME + old))
        self.assertFalse(glance.glance_exists(self._IMG_NAME))
        self.assertTrue(glance.glance_exists(self._IMG_NAME + old))
        self.assertTrue(glance.glance_rename(self._IMG_NAME + old, self._IMG_NAME))
        self.assertFalse(glance.glance_exists(self._IMG_NAME + old))
        self.assertTrue(glance.glance_exists(self._IMG_NAME))
        # TODO: 2 images ont le meme nom...
        # TODO: rename inexistent

    def test_glance_download(self):
        _RND1M_FILE = get_local_path('..', 'data', 'random_1M.bin')
        _DL_ED_FILE = os.path.join('/', 'tmp', self._IMG_NAME)

        if os.path.exists(_DL_ED_FILE):
            os.remove(_DL_ED_FILE)

        self.common_start(self._IMG_NAME, _RND1M_FILE)
        self.assertTrue(glance.glance_download(self._IMG_NAME, _DL_ED_FILE))
        self.assertTrue(os.path.exists(_DL_ED_FILE))
        self.assertTrue(utils.run(['cmp', _RND1M_FILE, _DL_ED_FILE])[0])
        os.remove(_DL_ED_FILE)
        self.assertFalse(os.path.exists(_DL_ED_FILE))
        self.assertFalse(glance.glance_download('', _DL_ED_FILE))
        self.assertFalse(os.path.exists(_DL_ED_FILE))
