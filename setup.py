#! /usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "Glancing",
    version = "0.1",
    packages = find_packages(),

    # metadata for upload to PyPI
    author = "Vincent Legoll",
    author_email = "vincent.legoll@idgrilles.fr",
    description = ("Helper tool for checking VM images and uploading "
                   "them into an openstack glance service"),
    license = "GPLv2",
    keywords = "openstack glance virtualization",
    # url = "http://example.com/HelloWorld/",   # project home page, if any
)
