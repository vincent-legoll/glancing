#. What is this
===============

This is a few helper scripts to ease importing VM images into an
OpenStack glance service. It can handle various kind of VM image
source metadata, as well as work directly with local files.

#. Features
===========

- Import images from: local file, download from an URL, use an image JSON
  metadata file from the StratusLab marketplace, or directly download the
  metadata from a given ID for that marketplace.

- Check image against multiple message digest algorithms to ensure no
  tampering with them has happened.

- Backup previous versions of an image when importing the new version

#. How to run
=============

Assuming your environment contains the appropriate variables & values for
connecting to a glance service, see in "Automated Testing" section below.

- Local file, without checksum verification:

    $ ./src/glancing.py image /tmp/cirros-0.3.4-i386-disk.img

- Download image from URL, check given MD5 message digest

    $ ./src/glancing.py url http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-i386-disk.img -s 79b4436412283bb63c2cba4ac796bcd9

- Download XML metadata from StatusLab marketplace, get the URL from this
  metadata, then get the image from the URL, and verify all the checksums
  that are available.

  This one is for a CentOS v7 image...

    $ ./src/glancing.py market KqU_1EZFVGCDEhX9Kos9ckOaNjB

- You have browsed the StratusLab marketplace, and found the right image
  for your project, downloaded its JSON metadata locally, then want to
  get that VM image:

    $ ./src/glancing.py json /tmp/KqU_1EZFVGCDEhX9Kos9ckOaNjB.json

You can use the "-d" or "--dry-run" CLI parameter to only download the VM
image file, verify the checksum(s) but not import into glance registry.

    $ ./src/glancing.py -d image /tmp/cirros-0.3.4-i386-disk.img -s 79b4436412283bb63c2cba4ac796bcd9

#. Get Help
===========

The ./src/glancing.py script CLI options are documented in-line, please
run it like the following to see the help:

    ./src/glancing.py --help

#. Automated Testing
====================

Both `nose` & `py.test` can be used to run the test suite

In order to launch all the automated tests, just use the included script,
which use `nose` to collect the tests to run:

    $ ./run_tests.sh

or just use:

    $ py.test

Or you can select only a single test to be run manually:

    $ ./run_tests.sh test/src/test_utils.py:UtilsRunTest.test_utils_run_true

First you give the test module test_XXX.py file, a colon, then the class,
a dot, then the method from that class.

The py.test way of doing manual test selection:

    $ py.test test/src/test_utils.py::UtilsRunTest::test_utils_run_true

The tests check for availability of a glance registry service to test
images uploading. Just populate the traditionnal OpenStack variables,
see environmentVars_. Or modify the ./test/openstack/admin.sh accordingly
before launching the test suite.

You can further extend the coverage of the test suite, by modifying the
following lines from ./test/src/test_glancing.py file. They enable more
tests, but will download a lot of big (huge) image files...

    _HEAVY_TESTS = False
    _HUGE_TESTS = False

In the run_tests.sh script you can also configure the usage of nose test
plugins for code coverage, pep8 conformance checking and profiling.

The code coverage results will be located, after a test run, in:

    ./cover/index.html

#. Environment variables
========================
.. _environmentVars:

You can set those to configure access to your local OpenStack Glance VM
image registry sevice:

    export OS_TENANT_NAME=admin_tenant
    export OS_USERNAME=admin_username
    export OS_PASSWORD=ADMIN_PASSWORD
    export OS_AUTH_URL=http://controller_node:35357/v2.0
    export OS_REGION_NAME="IPHC"
    export OS_CACERT="${HOME}/path/to/CNRS2.pem"
