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

cutOutHist <- function(data, l=1, r=Inf, type='h', col='blue') {
  if (r > length(data) ) {
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
  return (list(sample, abs(difs), abs(difs_difs))) # dubious 'abs'
}

gatheringInfo <- function(filename, sl_l, sl_r) {
  data <- dSamplesFromFile(filename)
  
  cutOutHist(data[[1]], l=sl_l, r=sl_r, type='l', col='green')
  cutOutHist(abs(data[[2]]), l=sl_l, r=sl_r)
  cutOutHist(data[[3]], l=sl_l, r=sl_r, col='red')
  
  return(data)
}

durationAt16khz <- function(start, end) {
  return(((end-start) / 16000) * 1000)
}

files <- sapply(c(1,2,3), FUN=function(ihateR) {sprintf('local/nan-ai-file-%d.wav', ihateR)})
slices <- matrix(data=c(34891,35050,41740,42056,1,Inf), byrow = TRUE, nrow = 3, ncol = 2)
widenSliceBy <- function(slice, wid=3000) {
  return( c(max(0,slice[1]-wid), slice[2]+wid) )
}
slices <- t(apply(slices, 1, FUN=widenSliceBy))

test_data <- matrix(cbind(files, slices), ncol=3, nrow=3) # in a perfect world this wouldn't be necessary

pdf("plots.pdf")

sideRes <- apply(test_data, 1, FUN=function(x) {
    gatheringInfo(
      filename = x[1],
      sl_l = as.numeric(x[2]), 
      sl_r = as.numeric(x[3])
      )
  })

sideRes <- apply(test_data, 1, FUN=function(x) {
  gatheringInfo(
    filename = x[1],
    0, Inf
  )
})

dev.off()