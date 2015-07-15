#! /usr/bin/env python

import os
import sys
import math
import pickle
import timeit
import argparse

import matplotlib.pyplot as plt
import matplotlib.markers

# Only usable in a script module, not in an imported package
# as sys.argv[0] will not be right, maybe use __file__ instead
def mod_path():
    ret_path = os.path.dirname(sys.argv[0])
    if not os.path.isabs(ret_path):
        ret_path = os.path.join(os.getcwd(), ret_path)
    return os.path.realpath(ret_path)

# Setup PYTHONPATH for multihash
sys.path.append(os.path.realpath(os.path.join(mod_path(), '..', '..', 'src')))

_SETUP = \
'''
import multihash
mh = multihash.multihash_%s(%s)
'''

_UNIT_PREFIX = ['', 'K', 'M', 'G', 'T', 'P']

def unit_prefix(n):
    if n == 0:
        return 0, ''
    exp = int(math.log(n, 2) / 10)
    return n / (2 ** (10 * exp)), _UNIT_PREFIX[exp]

def bench_one(fn, setup, repeats=1):
    return timeit.timeit('mh.hash_file("%s")' % fn, setup=setup, number=repeats)

def bench_files(files):
    lengths = []
    times_sh = []
    times_mh = {
# Uninteresting buffer sizes: too small
        32: [],
        64: [],
        128: [],
        512: [],
        1024: [],
        1024 * 4: [],
        1024 * 1024: [],
        10 * 1024 * 1024: [],
    }
    for fn in files:
        lengths.append(os.path.getsize(fn) / (1024 * 1024))
        times_sh.append(bench_one(fn, _SETUP % ('serial_exec', '')))
        for size, res in times_mh.iteritems():
            res.append(bench_one(fn, _SETUP % ('hashlib', 'block_size=%d' % size)))
    return lengths, times_sh, times_mh

def plotit(lengths, times_sh, times_mh):
    plt.title('Benchmark multiple hash computing implementations')
    plt.xlabel('File size in MB')
    plt.ylabel('Time in seconds')
    plt.rc('lines', linewidth=1, linestyle='-')

    # Prepare marker list
    mks = set(matplotlib.markers.MarkerStyle().markers.keys())
    # Remove unwanted ones
    mks -= set((None, 'None', '', ' ', '|', '_', '.', ',', '+', '-', 'd', 'x', '*'))
    mks = ['<', '>', '^', 'v', 'o', 'D', 's', 'p', 'h', ]
    assert len(mks) >= len(times_mh)

    # Experiment with logarithmic scale
    plotter = plt.semilogx # plt.plot

    # Plot serial exec data
    plotter(lengths, times_sh, label='serial exec', marker='*')

    # Plot parallel hashlib data, for each block size
    for size in sorted(times_mh.keys()):
        plotter(lengths, times_mh[size], marker=mks.pop(),
                 label='parallel hashlib, bs=%d%s' % unit_prefix(size))

    # Give some horizontal room
    #xmin, xmax = plt.xlim()
    #plt.xlim(0, xmax * 1.1)

    # Put legend in top left corner
    plt.legend(loc=2)

    # Save a visual
    plt.savefig('multihash.svg')

    # Display resulting figure
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Benchmark multihash')
    group = parser.add_mutually_exclusive_group(required=False)

    group.add_argument('-l', '--load', dest='load', metavar='FILE',
                       help='')
    group.add_argument('-s', '--store', dest='store', metavar='FILE',
                       help='')

    parser.add_argument(dest='files', metavar='FILE', nargs='*',
                       help='')

    args = parser.parse_args()

    if args.load:
        with open(args.load, 'rb') as fin:
            lengths, times_sh, times_mh = pickle.load(fin)
            plotit(lengths, times_sh, times_mh)
    else:
        if args.files:
            lengths, times_sh, times_mh = bench_files(files)
            if args.store:
                with open(args.store) as fout:
                    pickle.dump((lengths, times_sh, times_mh), fout)

if __name__ == '__main__':
    main()
