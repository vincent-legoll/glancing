#! /usr/bin/env python

from __future__ import print_function

import os
import json
import hashlib
import xml.etree.ElementTree as et

import decompressor

from utils import vprint

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

class MetaDataBase(object):

    def __init__(self):
        super(MetaDataBase, self).__init__()

    def get_name(self):
        md = self.data
        return '%s-%s-%s' % (md['os'], md['os-version'], md['os-arch'])

# Translate Stratuslab market place hash names to hashlib ones
def sl_to_hashlib(hash_name):
    return hash_name.replace('-', '').lower()

class MetaDataJson(MetaDataBase):

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

    _RETKEY_TO_CERN = {
        'bytes': "hv:size",
        'location': "hv:uri",
        'os': "sl:os",
        'os-arch': "sl:arch",
        'os-version': "sl:osversion",
    }

    def __init__(self, jsonfile, ident):
        super(MetaCern, self).__init__(jsonfile)
        self.all_images = {}
        self.get_all_images()
        self.data = None
        self.ident = ident

    def get_metadata(self):
        return self.all_images.get(self.ident, {})

    def get_all_images(self):
        il = self.json_obj["hv:imagelist"]["hv:images"]
        for img_h in il:
            img = img_h["hv:image"]
            ret = {
                'checksums': {},
                'format': 'raw',
                'compression': None,
            }
            ext = os.path.splitext(img["hv:uri"])[1]
            if ext in decompressor._EXT_MAP:
                ret['compression'] = ext.strip('.')
            for (key, val) in self._RETKEY_TO_CERN.iteritems():
                ret[key] = img[val]
            for algo in hashlib.algorithms:
                key = "sl:checksum:" + algo
                if key in img:
                    ret['checksums'][algo] = img[key]
            self.all_images[img["dc:identifier"]] = ret

class MetaStratusLabXml(MetaDataBase):
    '''Parse the metadata .xml file, from the stratuslab marketplace
       Extract interesting data: url and message digests
    '''

    def __init__(self, filename):
        super(MetaStratusLabXml, self).__init__()
        try:
            self.xml_obj = et.parse(filename)
        except et.ParseError as e:
            vprint('parse error')
            self.get_metadata = lambda: None
        self.data = { 'checksums': {} }

    def get_metadata(self):
        ns = StratusLabNS._NS_TO_URL_PREFIXES
        ret = self.data
        root = self.xml_obj.getroot()
        # StratusLab xml metadata files are not consistent:
        # if downloaded through the XML button or directly
        # through the url, there's an additionnal root tag
        if root.tag == 'metadata':
            rdf = root.find('rdf:RDF', ns)
        else:
            rdf = root
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
