#! /usr/bin/env python

# TODO: finish this setup, it is currently only half baked

import sys

from setuptools import setup, find_packages

setup(
    name = "Glancing",
    version = "0.1",

    packages = find_packages(),

    tests_require = ['nose', 'pytest', 'pytest-xdist'],

    # metadata for upload to PyPI
    author = "Vincent Legoll",
    author_email = "vincent.legoll@idgrilles.fr",
    description = ("Helper tool for checking VM images and uploading "
                   "them into an openstack glance service"),
    license = "GPLv3",
    keywords = "openstack glance virtualization",
    url = "http://www.france-grilles.fr/",
)
