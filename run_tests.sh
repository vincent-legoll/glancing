#!/bin/sh

PACKAGES="glancing,glance,multihash,metadata,decompressor,openstack_out,utils,tutils,test_glancing,test_multihash,test_metadata,test_decompressor,test_utils,test_tutils,test_glance,test_openstack_out"

COVERAGE_OPTS="--with-coverage --cover-branches --cover-html --cover-inclusive --cover-tests --cover-package=${PACKAGES}"
PROFILE_OPTS= # "--with-profile"
TISSUE_IGNORES="--tissue-ignore=E302,E501,E261,E201,E202,E241" # I disagree with those
TISSUE_OPTS="--with-tissue --cover-inclusive --tissue-package=${PACKAGES} ${TISSUE_IGNORES}" # pip install --user tissue

ALL_OPTS="${COVERAGE_OPTS} ${PROFILE_OPTS} ${TISSUE_OPTS}"

# If our local cloud is running, use it
ps faux | grep [c]7-ctrl > /dev/null 2>&1
if [ $? -eq 0 ]; then
  . ~/openstack/admin_local.sh
fi

nosetests --exe ${ALL_OPTS} $*
