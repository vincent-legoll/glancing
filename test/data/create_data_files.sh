#! /bin/sh

for i in 1 5 10 25 50 75 100 200 300 400 500 1000; do
  [ -f "random_${i}M.bin" ] || dd if=/dev/urandom of="random_${i}M.bin" bs=1M count=${i};
done
