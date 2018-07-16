from pylab import array
from scipy.io import wavfile
from scipy.stats import ks_2samp
from numpy.random import uniform
from math import floor
from itertools import groupby
import argparse
import numpy as np
import dotenv
from pathlib import Path

# ARGPARSE
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some audio files.')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
                        help='Audio file to be processed')
    parser.add_argument('--verbose', dest='verbose', action='store_const',
                        const=True, default=False,
                        help='Print debug info')
    parser.add_argument('--config', dest='config_file', action='store', default='.env',
                        help='Supersede constants in code from some file. Script uses .env as default anyways.')
    global args
    args = parser.parse_args()

    env_path = Path('.') / args.config_file
    dotenv.load(env_path)
    
    global DUR_THRESH
    global SILENCE_THRESH
    global TEST_COUNT
    global ALPHA_CUTOFF
    global ANOTHER_CUTOFF

    DUR_THRESH = float(dotenv.get("DUR_THRESH", 1.2))
    SILENCE_THRESH = float(dotenv.get("SILENCE_THRESH", 1e-02))
    TEST_COUNT = int(dotenv.get("TEST_COUNT", 3))
    ALPHA_CUTOFF = float(dotenv.get("ALPHA_CUTOFF", 0.1))
    ANOTHER_CUTOFF = float(dotenv.get("ANOTHER_CUTOFF", 0.3))

# imported and explained (sort of, kinda, I hope)
else:
    # "shortest distinguishable sound interval is 1.2ms" (Irwin & Purdy, 1982)
    DUR_THRESH = 1.2

    # one more for differentiating between signal and silence
    SILENCE_THRESH = 1e-02

    # this will be doubled, mind you
    TEST_COUNT = 3 

    # that p-value related thingy
    ALPHA_CUTOFF = 0.1
    ANOTHER_CUTOFF = 0.3 # a.k.a. ANOTHER magic constant

SAMPLE_RATE = 16000
SAMPLE_COUNT_THRESH = (DUR_THRESH / 1000) * SAMPLE_RATE # a.k.a. THE magic constant

def if_verbose_print(data):
    try:
        if args.verbose:
            print(data)
    except NameError: # if imported then 'args' is not in the namespace
        print(data)

if_verbose_print((
    "Using config: {}\n" +
    "DUR_THRESH = {}\n" +
    "SILENCE_THRESH = {}\n" +
    "TEST_COUNT = {}\n" +
    "ALPHA_CUTOFF = {}\n" +
    "ANOTHER_CUTOFF = {}\n"
).format(
    args.config_file if args else "(none)",
    DUR_THRESH,
    SILENCE_THRESH,
    TEST_COUNT,
    ALPHA_CUTOFF,
    ANOTHER_CUTOFF,
))
   
def read_sound_object(filename):
    global SAMPLE_RATE
    sampFreq, snd = wavfile.read(filename)
    if sampFreq != SAMPLE_RATE:
        print("Warning: overriding SAMPLE_RATE")
        SAMPLE_RATE = sampFreq

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

    # this filter ignores all short quiet ranges -> 'short' means smaller than MAGIC_CONSTANT
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
        TEST_COUNT *= 2 # we will be comparing only to one side -> so double up the effort!

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
        else:
            if_verbose_print("Marking as a pass: [{},{}]".format(left, right))
        
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
                if len(verdict[1])>1:
                    if_verbose_print("{} more potential regions: {}".format( len(verdict[1])-1, verdict[1] )) 

        except ValueError as e:
            print(PRINT_OUT.format(file, INVALID, "["+str(e)+"]"))

        except NonsensicalResult as e:
            print(PRINT_OUT.format(file, INVALID, "[ Internal error ]"))
        

    