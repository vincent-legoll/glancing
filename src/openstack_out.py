#! /usr/bin/env python

from __future__ import print_function

import os
import re
import sys
import json
import argparse

import utils
import openstack_out

re_sep_line = re.compile(r'^[+-]+$')

def parse_block(block, line_pattern_re=None, line_anti_pattern_re=None):
    header = []
    ret = []
    seps = 0
    length = 0
    for line in block.splitlines():
        if not line:
            continue
        if re_sep_line.match(line):
            seps += 1
            continue
        if seps == 0:
            continue
        elif seps == 3:
            break
        line_split = [i.strip() for i in line.split('|')][1:-1]
        ls_len = len(line_split)
        if seps == 1:
            header = line_split
            length = ls_len
        else: # if seps == 2:
            if line_pattern_re is not None:
                if not line_pattern_re.search(line):
                    continue
            if line_anti_pattern_re is not None:
                if line_anti_pattern_re.search(line):
                    continue
            if length == ls_len:
                ret.append(line_split)
            else:
                print('line "%s" has wrong number of columns %d, should'
                      ' be %d ' % (line, ls_len, length))
                continue

    return header, ret

def map_block(block):
    ret = {}
    h, b = parse_block(block)
    # Direct mapping
    if len(h) == 2:
        for i in range(len(b)):
            #if len(h) == len(b[i]): # Useless, parse_block ensures that
                ret[b[i][0]] = b[i][1]
    # Mapping to lists
    else: # if len(h) > 2:
        for i in range(len(b)):
            #if len(h) == len(b[i]): # Useless, parse_block ensures that
                ret[b[i][0]] = b[i][1:]
    return ret

def cli(sys_argv=sys.argv[1:]):
    desc_help = 'Select a part of an openstack command output'
    parser = argparse.ArgumentParser(description=desc_help)

    parser.add_argument('-p', '--pattern', dest='pattern', default=None,
                        nargs="?", metavar='STRING',
                        help='pattern to select lines. Can be a python'
                        ' regex. Searched in the whole line')

    parser.add_argument('-P', '--anti-pattern', dest='antipattern',
                         default=None, nargs="?", metavar='STRING',
                        help='pattern to deselect lines. Can be a python'
                        ' regex. Searched in the whole line')

    parser.add_argument('-c', '--column', dest='column', default=None,
                        nargs="?", metavar='NUMBER',
                        help='column # to get')

    parser.add_argument('-t', '--head', dest='head', default=None,
                        nargs="?", metavar='NUMBER',
            help='In case of multi line output, get the first N lines')

    parser.add_argument(dest='cmd', nargs="+", metavar='STRING',
                        help='openstack command, as a single or multiple'
                        ' strings, but separated from the other parameters'
                        ' with "--"')

    return parser.parse_args(sys_argv)

def get_field(sys_argv=sys.argv[1:]):

    # Handle CLI arguments
    args = cli(sys_argv=sys_argv)

    # Column selection
    col = 0
    if args.column is not None:
        col = int(args.column)

    # Lines selection
    head = None
    if args.head:
        head = int(args.head)

    # Lines selection
    pat = None
    if args.pattern:
        pat = re.compile(args.pattern)

    # Lines deselection
    apa = None
    if args.antipattern:
        apa = re.compile(args.antipattern)

    # Command to run, simple or multiple strings
    cmd = args.cmd
    if len(cmd) == 1 and type(cmd[0]) == str:
        cmd = cmd[0].split()

    # Run it, grab output
    ok, retcode, out, err = utils.run(cmd, out=True)
    if not ok:
        return ''

    # Parse the returned array
    headers, rows = openstack_out.parse_block(out, pat, apa)
    if not rows:
        return ''

    # Return the requested columns
    if len(headers) > col:
        return [row[col] for row in rows[:head]]

    return ''

def main(sys_argv=sys.argv[1:]):
    for i in get_field(sys_argv=sys_argv):
        print(i)

if __name__ == '__main__':
    main()
