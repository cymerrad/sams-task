#!/home/radek/Documents/python/sams-task/env/bin/python
from pylab import *
from scipy.io import wavfile

_EX_FILES = [
    "local/nan-ai-file-1.wav",
    "local/nan-ai-file-2.wav",
    "local/nan-ai-file-3.wav",
]

sampFreq, snd = wavfile.read(_EX_FILES[0])
print("sampFreq {}".format(sampFreq))
print("sound type {}".format(snd.dtype))

# convert to range [-1,1]
snd = snd / (2.**15)
print("shape {}".format(snd.shape))

timeArray = arange(0, snd.shape[0], 1)
timeArray = timeArray / sampFreq
timeArray = timeArray * 1000  # scale to milliseconds

plot(timeArray, snd, color='k')
ylabel('Amplitude')
xlabel('Time (ms)')
savefig('foo.png') # PLOTTING WON'T WORK ON MY MACHINE