CRUFT_HERE = .tox cover src/*.pyc test/src/*.pyc src/__pycache__ test/src/__pycache__ Glancing.egg-info

NPROC = grep -c ^processor /proc/cpuinfo

clean:
	rm -rf $(CRUFT_HERE) $(TEST_DATA_FILES) $(TEST_IMAGE_FILES)
	rm -rf $(CHECKSUM_FILES_MH) $(CHECKSUM_FILES_SYS)
	find . -type f -name .coverage -print0 | xargs -r -0 rm

test_files: test_data_files test_image_files

nosetests: test_files
	./run_tests.sh

pytests: test_files
	py.test -n `$(NPROC)`

tox: test_files
	tox

# Download TEST_IMAGE_FILES
TEST_IMAGE_DIR = test/images
TEST_IMAGE_FILE_NAMES = ttylinux-16.1-x86_64.img coreos_production_qemu_image.img \
	cirros-0.3.4-i386-disk.img cirros-0.3.4-x86_64-disk.img \
	cirros-MD5SUMS cirros-SHA1SUMS
TEST_IMAGE_FILES = $(foreach IMG,$(TEST_IMAGE_FILE_NAMES),$(TEST_IMAGE_DIR)/$(IMG))

test_image_files: $(TEST_IMAGE_FILES)

test/images/ttylinux-16.1-x86_64.img:
	curl http://appliances.stratuslab.eu/images/base/ttylinux-16.1-x86_64-base/1.0/ttylinux-16.1-x86_64.img.gz | gzip -dc > $@

test/images/coreos_production_qemu_image.img:
	curl http://stable.release.core-os.net/amd64-usr/current/coreos_production_qemu_image.img.bz2 | bzip2 -dc > $@

test/images/cirros-0.3.4-i386-disk.img:
	curl http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-i386-disk.img > $@

test/images/cirros-0.3.4-x86_64-disk.img:
	curl http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img > $@

test/images/cirros-MD5SUMS:
	curl http://download.cirros-cloud.net/0.3.4/MD5SUMS > $@

test/images/cirros-SHA1SUMS:
	sha1sum cirros-0.3.4-* > $@

# Create TEST_DATA_FILES
SIZES = 1 5 10 25 50 75 100 200 300 400 500 750 1000
TEST_DATA_FILES_SIZE = $(foreach SIZ,$(SIZES),test/data/random_$(SIZ)M.bin)
TEST_DATA_FILES_COMP = $(foreach ALG,gz bz2 zip,test/data/random_1M.bin.$(ALG))
TEST_DATA_FILES_TINY = test/data/zero_length.bin test/data/one_length.bin
TEST_DATA_FILES = $(TEST_DATA_FILES_SIZE) $(TEST_DATA_FILES_COMP) $(TEST_DATA_FILES_TINY)

test_data_files: $(TEST_DATA_FILES)

test/data/zero_length.bin:
	touch $@

test/data/one_length.bin:
	echo > $@

test/data/random_%M.bin:
	dd if=/dev/urandom of="test/data/random_$*M.bin" bs=1M count=$*

test/data/random_1M_gz.bin.gz:
	gzip -c < test/data/random_1M.bin > $@

test/data/random_1M_bz2.bin.bz2:
	bzip2 -c < test/data/random_1M.bin > $@

test/data/random_1M_zip.bin.zip:
	zip $@ test/data/random_1M.bin

toupper = $(shell echo "$(1)" | tr -s '[:lower:]' '[:upper:]')
tolower = $(shell echo "$(1)" | tr -s '[:upper:]' '[:lower:]')

CHECKSUM_ALGOS = md5 sha1 sha224 sha256 sha384 sha512
CHECKSUM_FILES_MH = $(foreach ALG,$(CHECKSUM_ALGOS),test/data/$(call toupper,$(ALG))SUMS)
CHECKSUM_FILES_SYS = $(foreach CHKSUM_FILE,$(CHECKSUM_FILES_MH),$(CHKSUM_FILE).txt)

test/data/%SUMS.txt: $(TEST_DATA_FILES)
	$(call tolower,$*)sum $(TEST_DATA_FILES) > $@

test/data/%SUMS: $(TEST_DATA_FILES)
	src/multihash.py -d test/data -f $(TEST_DATA_FILES)

# Check validity against system utilities generated files...
test_data_check: $(CHECKSUM_FILES_MH) $(CHECKSUM_FILES_SYS)
	for sum in test/data/*SUMS; do cmp $${sum} $${sum}.txt || exit 42; done

# Nose testing & plugins

PACKAGES = "glancing,glance,multihash,metadata,decompressor,openstack_out,utils,tutils,test_glancing,test_multihash,test_metadata,test_decompressor,test_utils,test_tutils,test_glance,test_openstack_out"

COVERAGE_OPTS = --with-coverage --cover-branches --cover-html --cover-inclusive --cover-tests --cover-package=$(PACKAGES)
PROFILE_OPTS = # --with-profile

# Tissue plugin : check code for pep8 compliance
# pip install --user tissue
# I disagree with those errors
TISSUE_IGNORES = --tissue-ignore=E302,E501,E261,E201,E202,E241,E402,E128
TISSUE_OPTS = # --with-tissue --cover-inclusive --tissue-package=${PACKAGES} ${TISSUE_IGNORES}

ALL_OPTS = $(COVERAGE_OPTS) $(PROFILE_OPTS) $(TISSUE_OPTS)

.PHONY: test
test:
	nosetests --exe ${ALL_OPTS} $*
