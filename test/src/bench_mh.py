#! /usr/bin/env python

import os
import sys
import math
import timeit

import matplotlib.pyplot as plt
import matplotlib.markers

_SETUP_PYPATH = '''\
import sys
sys.path += ["../../src"]
import multihash
'''

_SETUP = _SETUP_PYPATH + 'mh = multihash.multihash_%s(%s)'

def bench_one(fn, setup, repeats=1):
    return timeit.timeit('mh.hash_file("%s")' % fn, setup=setup, number=repeats)

_UNIT_PREFIX = ['', 'K', 'M', 'G', 'T', 'P']

#### HERE

def unit_prefix(n):
    exp = int(math.log(n, 2))
    return n / (2 ** exp), _UNIT_PREFIX[exp / 10]

def main():
    lengths = []
    times_sh = []
    times_mh = {
# Not interesting bufefr sizes: too small
#        32: [],
#        64: [],
#        128: [],
        512: [],
        1024: [],
        1024 * 4: [],
        1024 * 1024: [],
        10 * 1024 * 1024: [],
    }
    for fn in sys.argv[1:]:
        lengths.append(os.path.getsize(fn) / (1024 * 1024))
        times_sh.append(bench_one(fn, _SETUP % ('serial_exec', '')))
        for size, res in times_mh.iteritems():
            res.append(bench_one(fn, _SETUP % ('hashlib', 'block_size=%d' % size)))
    plotit(lengths, times_sh, times_mh)

def plotit(lengths, times_sh, times_mh):
    plt.title('Benchmark multiple hash computing implementations')
    plt.xlabel('File size in MB')
    plt.ylabel('Time in seconds')
    
    plt.rc('lines', linewidth=1, linestyle='-')

    mks = matplotlib.markers.MarkerStyle().markers.keys()
    mks.remove(None)
    mks.remove('None')
    mks.remove('')
    mks.remove(' ')

    plt.plot(lengths, times_sh, label='serial exec', marker=mks.pop())
    for size, times in times_mh.iteritems():
        plt.plot(lengths, times, label='parallel hashlib, bs=%d' % size, marker=mks.pop())

    xmin, xmax = plt.xlim()
    plt.xlim(0, xmax * 1.1)

    plt.legend(loc=2)
    plt.show()

if __name__ == '__main__':
    main()
