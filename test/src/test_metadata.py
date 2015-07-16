#! /usr/bin/env python

import sys

from utils import get_local_path

# Setup PYTHONPATH for metadata
sys.path.append(get_local_path('..', '..', 'src'))

import metadata

def MetaStratusLab_test():
    fn = 'PIDt94ySjKEHKKvWrYijsZtclxU.json'
    jsonfile = get_local_path('..', 'stratuslab', fn)
    f = open(jsonfile, 'rb')
    m = metadata.MetaStratusLab(f)
    md = m.get_metadata()
    assert 'url' in md
    assert md['url'] == \
    'http://appliances.stratuslab.eu/images/base/CentOS-7-Server-x86_64/1.1/CentOS-7-Server-x86_64.dsk.gz'
