#!/home/radek/Documents/python/sams-task/env/bin/python
from pylab import *
from scipy.io import wavfile

_EX_FILES = [
    "local/440_sine.wav",
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

s1 = snd[:,0] 

plot(timeArray, s1, color='k')
ylabel('Amplitude')
xlabel('Time (ms)')
savefig('plots/plot1.png') # PLOTTING WON'T WORK ON MY MACHINE

n = len(s1) 
p = fft(s1) # take the fourier transform 
nUniquePts = int(ceil((n+1)/2.0))
p = p[0:nUniquePts]
p = abs(p)

p = p / float(n) # scale by the number of points so that
                 # the magnitude does not depend on the length 
                 # of the signal or on its sampling frequency  
p = p**2  # square it to get the power 

# multiply by two (see technical document for details)
# odd nfft excludes Nyquist point
if n % 2 > 0: # we've got odd number of points fft
    p[1:len(p)] = p[1:len(p)] * 2
else:
    p[1:len(p) -1] = p[1:len(p) - 1] * 2 # we've got even number of points fft

freqArray = arange(0, nUniquePts, 1.0) * (sampFreq / n);
plot(freqArray/1000, 10*log10(p), color='k')
xlabel('Frequency (kHz)')
ylabel('Power (dB)')
savefig('plots/plot2.png')