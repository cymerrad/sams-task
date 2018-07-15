#!/home/radek/Documents/python/sams-task/env/bin/python
from pylab import *
from scipy.io import wavfile

# everything assuming 16kHz
SAMPLE_RATE = 16000
DUR_THRESH = 1.2

# two thresholds: delta (change in amp) and duration (shortest distinguishable is 1.2ms (Irwin & Purdy, 1982))
DELTA_THRESH = 1e-04
SAMPLE_COUNT_THRESH = (DUR_THRESH / 1000) * SAMPLE_RATE

# one more for differentiating between signal and silence
STATIC_THRESH = 5e-05

EX_FILES = [
    "local/nan-ai-file-1.wav",
    "local/nan-ai-file-2.wav",
    "local/nan-ai-file-3.wav",
    "local/440_sine.wav",
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
            if arr[i] < threshold:
                pass
            else:
                curr = False
                rngs.append((st, i))

        else:
            if arr[i] < threshold:
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