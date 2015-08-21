#! /usr/bin/env python

from __future__ import print_function

import json
import xml.etree.ElementTree as et

class StratusLabNS(object):

    _NS_TO_URL_PREFIXES = {
        'dcterms': "http://purl.org/dc/terms/",
        'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        'slreq': "http://mp.stratuslab.eu/slreq#",
        'slterms': "http://mp.stratuslab.eu/slterms#",
        'base': "http://mp.stratuslab.eu/",
    }

    _RETKEY_TO_NS_PREFIXES = {
        'os': 'slterms',
        'bytes': 'slreq',
        'format': 'dcterms',
        'os-arch': 'slterms',
        'location': 'slterms',
        'algorithm': 'slreq',
        'os-version': 'slterms',
        'compression': 'dcterms',
    }

# Translate Stratuslab market place hash names to hashlib ones
def sl_to_hashlib(hash_name):
    return hash_name.replace('-', '').lower()

class MetaDataJson(object):

    def __init__(self, filename):
        super(MetaDataJson, self).__init__()
        with open(filename, 'rb') as fileobj:
            try:
            self.json_obj = json.loads(fileobj.read())
            except ValueError as e:
                self.json_obj = None
                self.get_metadata = lambda: None
            if not type(self.json_obj) is dict:
                raise ValueError('Cannnot load json data from: ' + filename)
        self.data = { 'checksums': {} }

class MetaStratusLabJson(MetaDataJson):
    '''Parse the metadata .json file, from the stratuslab marketplace
       Extract interesting data: url and message digests
    '''

    _MDKEY_TO_RETKEY = {
        StratusLabNS._NS_TO_URL_PREFIXES[ns] + key: key
        for key, ns in StratusLabNS._RETKEY_TO_NS_PREFIXES.items()
    }

    def get_metadata(self):
        ret = self.data
        for val in self.json_obj.values():
            for key in val:
                retkey = self._MDKEY_TO_RETKEY.get(key)
                value = val[key][0]['value']
                if retkey:
                    if retkey != 'algorithm':
                        ret[retkey] = value
                    else:
                        ret['checksums'][sl_to_hashlib(value)] = (
                            val['http://mp.stratuslab.eu/slreq#value']
                            [0]['value'])
        return ret

class MetaCern(MetaDataJson):
    pass

class MetaStratusLabXml(object):
    '''Parse the metadata .xml file, from the stratuslab marketplace
       Extract interesting data: url and message digests
    '''

    def __init__(self, filename):
        super(MetaStratusLabXml, self).__init__()
        try:
            self.xml_obj = et.parse(filename)
        except et.ParseError as e:
            self.get_metadata = lambda: None
        self.data = { 'checksums': {} }

    def get_metadata(self):
        ns = StratusLabNS._NS_TO_URL_PREFIXES
        ret = self.data
        root = self.xml_obj.getroot()
        rdf = root.find('rdf:RDF', ns)
        desc = rdf.find('rdf:Description', ns)
        for cksum in desc.findall('slreq:checksum', ns):
            algo = cksum.find('slreq:algorithm', ns)
            val = cksum.find('slreq:value', ns)
            ret['checksums'][sl_to_hashlib(algo.text)] = val.text
        for key in StratusLabNS._RETKEY_TO_NS_PREFIXES.keys():
            if key == 'algorithm':
                continue
            mdkey = StratusLabNS._RETKEY_TO_NS_PREFIXES[key] + ':' + key
            node = desc.find(mdkey, ns)
            ret[key] = node.text
        return ret
