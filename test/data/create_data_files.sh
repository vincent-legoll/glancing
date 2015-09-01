#! /bin/sh

if [ ! -f zero_length.bin ]; then
  touch length_zero.bin
fi

if [ ! -f one_length.bin ]; then
  echo > length_one.bin
fi

for i in 1 5 10 25 50 75 100 200 300 400 500 750 1000; do
  [ -f "random_${i}M.bin" ] || dd if=/dev/urandom of="random_${i}M.bin" bs=1M count=${i};
done

if [ ! -f random_1M_gz.bin.gz ]; then
  cp -f random_1M.bin random_1M_gz.bin
  gzip random_1M_gz.bin
fi
rm -f random_1M_gz.bin

if [ ! -f random_1M_bz2.bin.bz2 ]; then
  cp -f random_1M.bin random_1M_bz2.bin
  bzip2 random_1M_bz2.bin
fi
rm -f random_1M_bz2.bin

if [ ! -f random_1M_zip.bin.zip ]; then
  cp -f random_1M.bin random_1M_zip.bin
  zip random_1M_zip.bin.zip random_1M_zip.bin
fi
rm -f random_1M_zip.bin

ALL_DATA_FILES="random_*.bin random_*.bin.*"

# One at a time
md5sum    ${ALL_DATA_FILES} > MD5SUMS.txt
sha1sum   ${ALL_DATA_FILES} > SHA1SUMS.txt
sha224sum ${ALL_DATA_FILES} > SHA224SUMS.txt
sha256sum ${ALL_DATA_FILES} > SHA256SUMS.txt
sha384sum ${ALL_DATA_FILES} > SHA384SUMS.txt
sha512sum ${ALL_DATA_FILES} > SHA512SUMS.txt

# Do all at once
../../src/multihash.py ${ALL_DATA_FILES}

# Check validity agains system utilities generated files...
for sum in *SUMS; do
  cmp ${sum} ${sum}.txt || exit 42;
done

# All is good ? Remove duplicate files
rm -f ./*SUMS.txt
