#!/bin/sh

COVERAGE_OPTS="--with-coverage --cover-branches --cover-html --cover-inclusive --cover-tests --cover-package=glancing,multihash,metadata,decompressor,utils,test_glancing,test_multihash,test_metadata,test_decompressor"
PROFILE_OPTS="" # --with-profile

# If our local cloud is running, use it
ps faux | grep [c]7-ctrl > /dev/null 2>&1
if [ $? -eq 0 ]; then
  . ~/openstack/cloud_auth_local.sh
fi

nosetests --exe ${COVERAGE_OPTS} ${PROFILE_OPTS} $*
