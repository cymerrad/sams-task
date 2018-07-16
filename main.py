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

TEST_COUNT = 5

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

def rle_binary(bits):
    return [ len(list(g)) for k,g in groupby(bits) ]

def inverse_rle(lengths, values):
    result = []
    for z in zip(lengths, values):
        result += z[0] * [ z[1] ]
    return result

def silent_ranges(rle, boolz):
    cur = 0
    ranges = []
    for z in zip(rle, boolz):
        if z[1] == True :
            ranges.append((cur, cur+z[0]))
        cur += z[0] # always move the head to the right

    return ranges

if __name__ == '__main__':
    snd = read_sound_object(EX_FILES[0])

    below = [ True if abs(x) < SILENCE_THRESH else False for x in snd ] # those are quiet values
    rle = rle_binary(below) # run length encoding

    first_is_true = below[0] == True 

    # this filter ignores all short quiet ranges -> 'short' means < SAMPLE_COUNT_THRESH
    new_rle_values = [ True if x > SAMPLE_COUNT_THRESH and i%2==(first_is_true^1) else False for i,x in enumerate(rle) ] # yeeeeah...
    filtered_below = inverse_rle(rle, new_rle_values)
    filtered_rle = rle_binary(filtered_below)

    first_is_true = filtered_below[0] == True 
    last_is_true = first_is_true if len(filtered_rle)%2==1 else first_is_true^True

    filtered_rle_values = [ first_is_true if i%2==0 else first_is_true^True for i in range(len(filtered_rle))]

    rngs = silent_ranges(filtered_rle, filtered_rle_values) # FIXME: horrendously wrong

    assert len(rngs) > 2

    silencio = []
    if first_is_true:
        silencio += [ rngs[0] ]
        rngs = rngs[1:]
    if last_is_true:
        silencio += [ rngs[-1] ]
        rngs = rngs[:-1]       

    if len(silencio):
        TEST_COUNT *= 2 # double up the effort!

    print("\nComparing samples from ranges ({}) against ({})".format(
        ", ".join( [ "[{},{}]".format(x[0], x[1]) for x in silencio ] ),
        ", ".join( [ "[{},{}]".format(x[0], x[1]) for x in rngs ] ),
        ))

    for rr in rngs:
        comp_tests = []
        for t_number in range(TEST_COUNT):
            for sil in silencio:
                comp_tests += [compare_with_random_sample(rr, sil, snd)]

        print("\nSlice [{}:{}]\n{}".format(rr[0],rr[1], "\n".join( [ "\t{}".format(x) for x in comp_tests ] )))
