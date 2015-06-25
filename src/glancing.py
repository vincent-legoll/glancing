#! /usr/bin/env python3

import sys
import json
import argparse
import subprocess

def do_argparse():
    parser = argparse.ArgumentParser(description='Import checked VM images into glance')
    parser.add_argument('files', metavar='FILE', type=argparse.FileType('r'), nargs='+',
                       help='a .json file describing a VM, from the StratusLab marketplace (https://marketplace.stratuslab.eu)')
    args = parser.parse_args()
    return args.files

def check_glance_availability():
    try:
        ret = subprocess.call(['glance', '--version'],
                              stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        if ret != 0:
            print("%s: Cannot execute 'glance', please check it is properly"
                  " installed." % (sys.argv[0],), file=sys.stderr)
            sys.exit(ret)
    except FileNotFoundError as e:
        print("%s: Cannot execute 'glance', please check it is properly"
              " installed, and available in your PATH environment "
              "variable." % (sys.argv[0],), file=sys.stderr)
        sys.exit(-1)

def handle_one_file(f):
    tmp = json.loads(f.read())
    f.close()
    md5 = None
    url = None
    if type(tmp) is dict:
        for val in tmp.values():
            for key in val.keys():
                if key == "http://mp.stratuslab.eu/slreq#algorithm":
                    if val[key][0]['value'] == 'MD5':
                        md5 = val['http://mp.stratuslab.eu/slreq#value'][0]['value']
                        if url is not None:
                            return md5, url
                elif key == 'http://mp.stratuslab.eu/slterms#location':
                    url = val['http://mp.stratuslab.eu/slterms#location'][0]['value']
                    if md5 is not None:
                        return md5, url
    return md5, url

def main():
    files = do_argparse()
    check_glance_availability()
    for f in files:
        ret = handle_one_file(f)
        print(ret)

if __name__ == '__main__':
    main()
