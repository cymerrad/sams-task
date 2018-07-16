#!/home/radek/Documents/python/sams-task/env/bin/python
from pylab import *
from scipy.io import wavfile
from scipy.stats import ks_2samp
from numpy.random import uniform
from math import floor
from itertools import groupby
import numpy

# everything assuming 16kHz
SAMPLE_RATE = 16000
DUR_THRESH = 1.2

# two thresholds: delta (change in amp) and duration (shortest distinguishable is 1.2ms (Irwin & Purdy, 1982))
DELTA_THRESH = 1e-04
SAMPLE_COUNT_THRESH = (DUR_THRESH / 1000) * SAMPLE_RATE # a.k.a. THE magic constant

# one more for differentiating between signal and silence
STATIC_THRESH = 5e-05
SILENCE_THRESH = 5e-04

EX_FILES = [
    "local/nan-ai-file-1.wav",
    "local/nan-ai-file-2.wav",
    "local/nan-ai-file-3.wav",
]

def read_sound_object(filename):
    sampFreq, snd = wavfile.read(filename)
    snd = snd / (2.**15)
    if len(snd.shape) > 1: # more than one channel
        snd = snd[:,0]
    return snd

def ranges_below(threshold, arr):
    rngs = []
    i = 0
    curr = False
    st = 0
    while i < len(arr):
        if curr:
            if abs(arr[i]) < threshold:
                pass
            else:
                curr = False
                rngs.append((st, i))

        else:
            if abs(arr[i]) < threshold:
                curr = True
                st = i
            else:
                pass
        i += 1

    if curr:
        rngs.append((st,i+1))

    return rngs

def ranges_below2(threshold, threshold_delta, arr):
    rngs = []
    i = 0
    curr = False
    st = 0
    delta = 0
    while i < len(arr):
        delta = arr[i] - arr[i-1] # loop around at first element
        if curr:
            if abs(arr[i]) < threshold and abs(delta) < threshold_delta:
                pass
            else:
                curr = False
                rngs.append((st, i))

        else:
            if abs(arr[i]) < threshold and abs(delta) < threshold_delta:
                curr = True
                st = i
            else:
                pass
        i += 1

    if curr:
        rngs.append((st,i+1))

    return rngs

def random_range_from_of_size(l_range, r_range, range_size):
    if (range_size > r_range - l_range):
        raise IndexError

    left = floor(uniform(l_range, r_range - range_size + 1))
    right = left + range_size
    return (left,right)

def compare_with_random_sample(tested, test_source, data):
    rand_range = random_range_from_of_size(test_source[0], test_source[1], (tested[1]-tested[0]) )
    return ks_2samp(data[tested[0]:tested[1]], data[rand_range[0]:rand_range[1]])

def runs_of_ones_array(bits):
  # make sure all runs of ones are well-bounded
  bounded = numpy.hstack(([0], bits, [0]))
  # get 1 at run starts and -1 at run ends
  difs = numpy.diff(bounded)
  run_starts, = numpy.where(difs > 0)
  run_ends, = numpy.where(difs < 0)
  return run_ends - run_starts

def summarise_into_ranges(rle, boolz):
    state = True
    cur = 0
    ranges = []
    for z in zip(rle, boolz):
        if z[1] != state: # changed state
            ranges.append((cur, cur+z[0]))
            state = not state
        cur += z[0]
    return ranges

if __name__ == '__main__':
    snd = read_sound_object(EX_FILES[0])
    below = ranges_below(SILENCE_THRESH, snd)
    rle = runs_of_ones_array(below)

    # TODO this is not verbatim from R code
    long_below = [ True if x > SAMPLE_COUNT_THRESH and i%2==0 else False for i,x in enumerate(rle) ] # yeeeeah...

    rngs = [ x for x in below if x[1] - x[0] > SAMPLE_COUNT_THRESH ]

    assert len(rngs) > 2

    intro = rngs[0]
    outro = rngs[-1]
    rngs = rngs[1:-1]

    for rr in rngs:
        comp_tests = []
        for i in range(3):
            comp_tests += [compare_with_random_sample(rr, intro, snd)]

        for i in range(3):
            comp_tests += [compare_with_random_sample(rr, outro, snd)]

        print("\nSlice [{}:{}]\n{}".format(rr[0],rr[1], "\n".join( [ "\t{}".format(x) for x in comp_tests ] )))
