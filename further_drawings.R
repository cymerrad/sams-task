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

cutOutHist <- function(data, l=0, r=Inf, type='h', col='blue') {
  if (r==Inf) {
    r=length(data)
  }
  d <- data[l:r]
  # timeArray <- (0:(length(data)-1)) / sndObj@samp.rate
  # timeArray <- timeArray * 1000 #scale to milliseconds
  xx <- l + (0:(length(d)-1))
  plot(xx, d, type=type, col=col, xlab='Step', ylab='Value')
}

gatheringInfo <- function(filename) {
  sample <-sampleSoundObject(readWave(filename))
  cutOutHist(sample, type='l', col='green')
  difs <- diff(sample)
  cutOutHist(abs(difs))
  difs_difs <- diff(difs)
  cutOutHist(difs_difs, col='red')
  return (c(difs, difs_difs))
}

files <- sapply(c(1,2,3), FUN=function(ihateR) {sprintf('local/nan-ai-file-%d.wav', ihateR)})
sideRes <- sapply(files, FUN=gatheringInfo)