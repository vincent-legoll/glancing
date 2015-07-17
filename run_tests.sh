#!/bin/sh

COVERAGE_OPTS="--with-coverage --cover-branches --cover-html --cover-inclusive --cover-tests --cover-package=glancing,multihash,metadata,decompressor,utils,test_glancing,test_multihash,test_metadata,test_decompressor"

nosetests --exe ${COVERAGE_OPTS}
