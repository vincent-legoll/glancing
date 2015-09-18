Image manager tasks

1. Get base image
=================

wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img
wget -O cirros-MD5SUMS http://download.cirros-cloud.net/0.3.4/MD5SUMS
md5sum -c cirros-MD5SUMS 2>&1 | grep cirros-0.3.4-x86_64-disk.img     
cirros-0.3.4-x86_64-disk.img: OK

2. Modify it
============

or not...

3. Check it for security
========================

TODO

4. Create SL metadata
=====================

Install StratusLab marketplace CLI tools
----------------------------------------

Official documentation is here: [SLMP]

```
[sudo] pip install [--user] stratuslab-client
```

Create metadata
---------------

stratus-build-metadata \
  --author='Vincent Legoll' \
  --os=cirros \
  --os-version=0.3.4 \
  --os-arch=x86_64 \
  --title='CirrOS v0.3.4 for x86_64' \
  --location=http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img \
  cirros-0.3.4-x86_64-disk.img

Edit
----

<dcterms:description>
    Cloud testing image:
    - minimal functionality
    - minimal size
    - minimal security (widely known password).

    Do not use for production !
</dcterms:description>

Sign & endorse
--------------

stratus-sign-metadata \
    --p12-cert Grid2FR.p12 \
    --output cirros-0.3.4-x86_64-base-.sign.xml \
    cirros-0.3.4-x86_64-base-.xml
    Metadata file successfully signed: cirros-0.3.4-x86_64-base-.sign.xml

Validate
--------

stratus-validate-metadata cirros-0.3.4-x86_64-base-.sign.xml 
Valid: cirros-0.3.4-x86_64-base-.sign.xml

Upload to SL market
-------------------

stratus-upload-metadata \
    --marketplace-endpoint=https://marketplace.stratuslab.eu/marketplace/metadata \
    cirros-0.3.4-x86_64-base-.sign.xml

6. Add to signed image list
===========================

echo 'VMID' >> ${quattor}/etc/glance-manager/image_list.txt

7. Push updated image list to quattor
=====================================

- svn push
- svn pre-commit-hook: changelog
- svn pre-commit-hook: automated security-check (grab from glancepush)

8. Let sites get it
===================

- Cron: glance_manager.py
- or quattor-trigger ?
- ML: changelog

9. References
=============

[SLMP] http://www.stratuslab.eu/fp7/doku.php/tutorial:marketplace.html
