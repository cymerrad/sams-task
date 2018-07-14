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

dSamplesFromFile <- function(filename) {
  sample <-sampleSoundObject(readWave(filename))
  difs <- diff(sample)
  difs_difs <- diff(abs(difs))
  return (c(sample, abs(difs), abs(difs_difs))) # dubious 'abs'
}

gatheringInfo <- function(filename, sl_l, sl_r) {
  data <- dSamplesFromFile(filename)
  
  cutOutHist(data[1], l=sl_l, r=sl_r, type='l', col='green')
  cutOutHist(abs(data[2]), l=sl_l, r=sl_r)
  cutOutHist(data[3], l=sl_l, r=sl_r, col='red')
  
}

files <- sapply(c(1,2,3), FUN=function(ihateR) {sprintf('local/nan-ai-file-%d.wav', ihateR)})
slices <- matrix(data=c(34891,35050,41740,42056,0,Inf), byrow = TRUE, nrow = 3, ncol = 2)
widenSliceBy <- function(slice, wid=500) {
  return( c(max(0,slice[1]-wid), slice[2]+wid) )
}
slices <- t(apply(slices, 1, FUN=widenSliceBy))

test_data <- cbind(files, slices)

sideRes <- apply(test_data, 1, FUN=function(x) {gatheringInfo(x[1],numeric(x[2]), numeric(x[3]))} )

