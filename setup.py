#! /usr/bin/env python

import sys

from setuptools import setup, find_packages

# handle python 3.x
# FIXME: not working
if sys.version_info >= (3,):
    use_2to3 = True
else:
    use_2to3 = False

setup(
    name = "Glancing",
    version = "0.1",
    
    packages = find_packages(),

    use_2to3 = use_2to3,

    tests_require = ['nose', 'pytest', 'pytest-xdist'],

    # metadata for upload to PyPI
    author = "Vincent Legoll",
    author_email = "vincent.legoll@idgrilles.fr",
    description = ("Helper tool for checking VM images and uploading "
                   "them into an openstack glance service"),
    license = "GPLv2",
    keywords = "openstack glance virtualization",
    # url = "http://example.com/HelloWorld/",   # project home page, if any
)
