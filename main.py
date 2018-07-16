#!/home/radek/Documents/python/sams-task/env/bin/python
from pylab import *
from scipy.io import wavfile
from scipy.stats import ks_2samp
from numpy.random import uniform
from math import floor
from itertools import groupby
import argparse
import numpy as np

# everything assuming 16kHz
SAMPLE_RATE = 16000
DUR_THRESH = 1.2

# two thresholds: delta (change in amp) and duration (shortest distinguishable is 1.2ms (Irwin & Purdy, 1982))
DELTA_THRESH = 1e-04
SAMPLE_COUNT_THRESH = (DUR_THRESH / 1000) * SAMPLE_RATE # a.k.a. THE magic constant

# one more for differentiating between signal and silence
SILENCE_THRESH = 5e-04

TEST_COUNT = 3 # this will be doubled, mind you

ALPHA_CUTOFF = 0.5
ANOTHER_CUTOFF = 0.3

# ARGPARSE
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some audio files.')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
                        help='Audio file to be processed')
    parser.add_argument('--verbose', dest='verbose', action='store_const',
                        const=True, default=False,
                        help='Print debug info')
    global args
    args = parser.parse_args()


def if_verbose_print(data):
    try:
        if args.verbose:
            print(data)
    except NameError: # if imported then 'args' is not in the namespace
        print(data)

def read_sound_object(filename):
    sampFreq, snd = wavfile.read(filename)
    snd = snd / (2.**15) # TODO: dependant on integer type
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

class NonsensicalResult(Exception):
    pass

def data_gather_procedure(samples_arr, TEST_COUNT=TEST_COUNT, SILENCE_THRESH=SILENCE_THRESH, MAGIC_CONSTANT=SAMPLE_COUNT_THRESH):
    below = [ True if abs(x) < SILENCE_THRESH else False for x in samples_arr ] # those are quiet values
    rle = rle_binary(below) # run length encoding

    first_is_true = below[0] == True 

    # this filter ignores all short quiet ranges -> 'short' means < MAGIC_CONSTANT
    new_rle_values = [ True if x > MAGIC_CONSTANT and i%2==(first_is_true^1) else False for i,x in enumerate(rle) ] # yeeeeah...
    filtered_below = inverse_rle(rle, new_rle_values)
    filtered_rle = rle_binary(filtered_below)

    first_is_true = filtered_below[0] == True 
    last_is_true = first_is_true if len(filtered_rle)%2==1 else first_is_true^True

    filtered_rle_values = [ first_is_true if i%2==0 else first_is_true^True for i in range(len(filtered_rle))]

    rngs = silent_ranges(filtered_rle, filtered_rle_values)

    silencio = []
    if first_is_true:
        silencio += [ rngs[0] ]
        rngs = rngs[1:]
    if last_is_true:
        silencio += [ rngs[-1] ]
        rngs = rngs[:-1]       

    if len(silencio):
        TEST_COUNT *= 2 # we will be comparing only to one side -> double up the effort!

    if_verbose_print("\nComparing samples from ranges ({}) against ({})".format(
        ", ".join( [ "[{},{}]".format(x[0], x[1]) for x in silencio ] ),
        ", ".join( [ "[{},{}]".format(x[0], x[1]) for x in rngs ] ),
        ))

    result = []
    for rr in rngs:
        comp_tests = []
        for _ in range(TEST_COUNT):
            for sil in silencio:
                comp_tests += [compare_with_random_sample(rr, sil, samples_arr)]

        result.append((rr[0], rr[1], comp_tests))

    return result

def data_analyse_procedure(data, ALPHA_CUTOFF=ALPHA_CUTOFF, ANOTHER_MAGIC_CONSTANT=ANOTHER_CUTOFF):
    # some arbitrary decisions will have to be made
    # e.g. when is the data in favour of accepting the data?
    errors = []

    for left, right, stats in data:
        s = array([ x.pvalue for x in stats ])

        if len(s) == 0:
            continue

        if_verbose_print("\nSample [{}:{}] p-values:\n{}".format(left,right, "\n".join( [ "\t{:f}".format(x) for x in s ] )))

        in_favour, = np.where( s > ALPHA_CUTOFF )

        if ( (len(in_favour) / len(s)) > ANOTHER_MAGIC_CONSTANT ): # idk how to make that decision
            if_verbose_print("Marking as an error: [{},{}]".format(left, right))
            errors.append( (left, right) )
        
    if len(errors) > 0:
        return (False, errors)

    return (True,)


VALID = "VALID"
INVALID = "INVALID"
PRINT_OUT = "{}\t{}\t{}"

if __name__ == '__main__':
    for file in args.files:
        try:
            sample_arr = read_sound_object(file)
            res = data_gather_procedure(sample_arr)
            verdict = data_analyse_procedure(res)
            if verdict[0]:
                print(PRINT_OUT.format(file, VALID, ""))
            else:
                print(PRINT_OUT.format(
                    file, 
                    INVALID, 
                    "[{},{}]".format(*verdict[1][0]), # only the first one
                )) 

        except ValueError as e:
            print(PRINT_OUT.format(file, INVALID, "["+str(e)+"]"))

        except NonsensicalResult as e:
            print(PRINT_OUT.format(file, INVALID, "[ Internal error ]"))
        

    