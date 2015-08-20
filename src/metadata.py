#! /usr/bin/env python

from __future__ import print_function

import json
import xml.etree.ElementTree as et

# Translate Stratuslab market place hash names to hashlib ones
def sl_to_hashlib(hash_name):
    return hash_name.replace('-', '').lower()

class MetaDataSL(object):
    
    def __init__(self):
        super(MetaDataSL, self).__init__()
        self.MDKEY_TO_RETKEY = {
            item[1] + item[0]: item[0] for item in
            self._RETKEY_TO_MDKEY_PREFIXES.iteritems()
        }

    def retkey_to_mdkey(self, key):
        return self._RETKEY_TO_MDKEY_PREFIXES[key] + key

    def mdkey_to_retkey(self, key):
        return self.MDKEY_TO_RETKEY.get(key)

class MetaDataJson(object):

    def __init__(self, filename):
        super(MetaDataJson, self).__init__()
        with open(filename, 'rb') as fileobj:
            self.json_obj = json.loads(fileobj.read())
            if not type(self.json_obj) is dict:
                raise ValueError('Cannnot load json data from: ' + filename)
        self.data = { 'checksums': {} }

class MetaStratusLab(MetaDataJson, MetaDataSL):
    '''Parse the metadata .json file, from the stratuslab marketplace
       Extract interesting data: url and message digests
    '''

    _RETKEY_TO_MDKEY_PREFIXES = {
        'os': 'http://mp.stratuslab.eu/slterms#',
        'bytes': 'http://mp.stratuslab.eu/slreq#',
        'format': 'http://purl.org/dc/terms/',
        'os-arch': 'http://mp.stratuslab.eu/slterms#',
        'location': 'http://mp.stratuslab.eu/slterms#',
        'algorithm': 'http://mp.stratuslab.eu/slreq#',
        'os-version': 'http://mp.stratuslab.eu/slterms#',
        'compression': 'http://purl.org/dc/terms/',
    }

    def get_metadata(self):
        ret = self.data
        for val in self.json_obj.values():
            for key in val:
                retkey = self.mdkey_to_retkey(key)
                value = val[key][0]['value']
                if retkey:
                    ret[retkey] = value
                elif key == self.retkey_to_mdkey('algorithm'):
                    algo = sl_to_hashlib(value)
                    ret['checksums'][algo] = val['http://mp.stratuslab.eu/slreq#value'][0]['value']
        return ret

class MetaCern(MetaDataJson):
    pass

class MetaStratusLabXml(MetaDataSL):
    '''Parse the metadata .xml file, from the stratuslab marketplace
       Extract interesting data: url and message digests
    '''

    _RETKEY_TO_MDKEY_PREFIXES = {
        'os': 'slterms:',
        'bytes': 'slreq:',
        'format': 'dcterms:',
        'os-arch': 'slterms:',
        'location': 'slterms:',
        'algorithm': 'slreq:',
        'os-version': 'slterms:',
        'compression': 'dcterms:',
    }

    def __init__(self, filename):
        super(MetaStratusLabXml, self).__init__()
        self.xml_obj = et.parse(filename)
        self.data = { 'checksums': {} }

    def get_metadata(self):
        root = self.xml_obj.getroot()
        md = root.find('metadata')
        desc = md.find('rdf:Description')
        for cksum in desc.findall('slreq:checksum'):
            algo = cksum.find('slreq:algorithm')
            val = cksum.find('slreq:value')
            ret['checksums'][algo.text] = val.text
        for key in self._RETKEY_TO_MDKEY_PREFIXES.keys():
            md_key = retkey_to_mdkey(key)
            node = desc.find(md_key)
            ret[key] = node.text
        return ret
