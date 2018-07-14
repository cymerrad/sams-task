library(tuneR)

# sndObj <- readWave('local/nan-ai-file-1.wav')
# l = length(sndObj@left)
# s1 <- sndObj@left
# s1 <- s1 / 2^(sndObj@bit -1)
# timeArray <- (0:(l-1)) / sndObj@samp.rate
# timeArray <- timeArray * 1000 #scale to milliseconds
# plot(timeArray, s1, type='l', col='blue', xlab='Time (ms)', ylab='Amplitude') 

sampleSoundObject <- function(sndObj) {
  l = length(sndObj@left)
  s1 <- sndObj@left
  s1 <- s1 / 2^(sndObj@bit -1)
  return(s1)  
}

cutOutHist <- function(data, l=0, r=Inf, type='h') {
  if (r==Inf) {
    r=length(data)
  }
  d <- data[l:r]
  # timeArray <- (0:(length(data)-1)) / sndObj@samp.rate
  # timeArray <- timeArray * 1000 #scale to milliseconds
  xx <- l + (0:(length(d)-1))
  plot(xx, d, type, col='blue', xlab='Step', ylab='Value')
}
s1 <- sampleSoundObject(readWave('local/nan-ai-file-1.wav'))
difs <- diff(s1)

cutOutHist(s1, 34000, 36000, type='l')
cutOutHist(difs, 34000, 36000)

cutOutHist(s1, 34750, 35250, type='l')
cutOutHist(difs, 34750, 35250)

cutOutHist(abs(difs), 31000, 36000)
cutOutHist(abs(difs), 34750, 35250)


correct <-sampleSoundObject(readWave('local/nan-ai-file-3.wav'))
difs_correct <- diff(correct)
cutOutHist(difs_correct)
