#! /usr/bin/env python3

import sys
import json
import argparse
import subprocess

def do_argparse():
    parser = argparse.ArgumentParser(description='Import VM images into glance, and verify checksum(s)')
    
    parser.add_argument('-f', '--fullcheck', action='store_true',
                       help='verify all available checksums, not just md5')
    parser.add_argument('files', metavar='FILE', type=argparse.FileType('r'), nargs='+',
                       help='a .json file describing a VM, from the StratusLab marketplace (https://marketplace.stratuslab.eu)')

    args = parser.parse_args()
    return args

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
    ret = {}
    if type(tmp) is dict:
        for val in tmp.values():
            # Early exit in case we found all interesting checksums
            if len(ret) == 5:
                return ret
            for key in val.keys():
                if key == 'http://mp.stratuslab.eu/slterms#location':
                    ret['url'] = val['http://mp.stratuslab.eu/slterms#location'][0]['value']
                elif key == "http://mp.stratuslab.eu/slreq#algorithm":
                    algo = val[key][0]['value']
                    ret[algo] = val['http://mp.stratuslab.eu/slreq#value'][0]['value']
    return ret

def main():
    args = do_argparse()
    check_glance_availability()
    for f in args.files:
        ret = handle_one_file(f)
        print(ret)

if __name__ == '__main__':
    main()
