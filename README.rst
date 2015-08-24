* What is this

TODO

* How to run

TODO

* Get Help

TODO

* Automated Testing:

In order to launch all the automated tests, just use the included script:

    $ ./run_tests.sh

Or you can select only a single test to be run manually:

    $ ./run_tests.sh test/src/test_glancing.py:TestGlancingMetadata.glancing_test_metadata_cirros_import_no_cksum

First you give the test module test_XXX.py file, a colon, then the class,
a dot, then the method from that class.

The tests attempt to use a glance service to test images uploading, just
populate the traditionnal OpenStack variables:

    export OS_TENANT_NAME=admin
    export OS_USERNAME=admin_account
    export OS_PASSWORD=ADMIN_PASSWORD
    export OS_AUTH_URL=http://ctrl:35357/v2.0

Or modify the ./test/openstack/admin.sh accordingly before launching the
test suite.

You can further extend the coverage, by modifying the following lines from
./test/src/test_glancing.py file. They enable more tests, but will download
a lot of big files...

    _HEAVY_TESTS = False
    _HUGE_TESTS = False

In ./run_tests.sh script you can also configure the usage of nose test
plugins for code coverage, pep8 conformance checking and profiling.

The code coverage results will be located, after a test run, in :

    ./cover/index.html
