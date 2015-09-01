#!/bin/sh

if [ ! -f ttylinux-16.1-x86_64.img ]; then
    wget http://appliances.stratuslab.eu/images/base/ttylinux-16.1-x86_64-base/1.0/ttylinux-16.1-x86_64.img.gz
    gunzip ttylinux-16.1-x86_64.img.gz
fi

if [ ! -f coreos_production_qemu_image.img ]; then
    wget http://stable.release.core-os.net/amd64-usr/current/coreos_production_qemu_image.img.bz2
    bunzip2 coreos_production_qemu_image.img.bz2
fi

if [ ! -f cirros-0.3.4-i386-disk.img ]; then
    wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-i386-disk.img
fi

if [ ! -f cirros-0.3.4-x86_64-disk.img ]; then
    wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img
fi

if [ ! -f cirros-MD5SUMS ]; then
    wget -O cirros-MD5SUMS http://download.cirros-cloud.net/0.3.4/MD5SUMS
fi
