#! /bin/sh

for i in 1 5 10 25 50 75 100 200 300 400 500 750 1000; do
  [ -f "random_${i}M.bin" ] || dd if=/dev/urandom of="random_${i}M.bin" bs=1M count=${i};
done

if [ -f random_1M_gz.bin.gz ]; then
  cp -f random_1M.bin random_1M_gz.bin
  gzip random_1M_gz.bin
fi

if [ -f random_1M_bz2.bin.bz2 ]; then
  cp -f random_1M.bin random_1M_bz2.bin
  bzip2 random_1M_bz2.bin
fi
