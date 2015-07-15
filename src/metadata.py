#! /usr/bin/env python

from __future__ import print_function

import json

_URLKEY_TO_RETKEY = {
    'http://mp.stratuslab.eu/slterms#location':   'url',
    'http://purl.org/dc/terms/compression':       'compression',
    'http://purl.org/dc/terms/format':            'diskformat',
    'http://mp.stratuslab.eu/slterms#os':         'ostype',
    'http://mp.stratuslab.eu/slterms#os-arch':    'osarch',
    'http://mp.stratuslab.eu/slterms#os-version': 'osver',
    'http://mp.stratuslab.eu/slreq#bytes':        'size',
}

# Translate Stratuslab market place hash names to hashlib ones
def sl_to_hashlib(hash_name):
    return hash_name.replace('-', '').lower()

class MetaStratusLab(object):
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.data = { 'checksums': {} }

    # Parse the metadata .json file, from the stratuslab marketplace
    # Extract interesting data: url and message digests
    def get_metadata(self):
        tmp = json.loads(self.fileobj.read())
        self.fileobj.close()
        ret = self.data
        if type(tmp) is dict:
            for val in tmp.values():
                for key in val:
                    value = val[key][0]['value']
                    if key in _URLKEY_TO_RETKEY:
                        ret[_URLKEY_TO_RETKEY[key]] = value
                    elif key == "http://mp.stratuslab.eu/slreq#algorithm":
                        algo = sl_to_hashlib(value)
                        ret['checksums'][algo] = val['http://mp.stratuslab.eu/slreq#value'][0]['value']
        return ret

class MetaEGI(object):
    pass

def main():
    fn = 'PIDt94ySjKEHKKvWrYijsZtclxU.json'
    f = open('../test/stratuslab/' + fn, 'rb')
    m = MetaStratusLab(f)
    print(m.get_metadata())

if __name__ == '__main__':
    main()
