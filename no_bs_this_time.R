library(tuneR)

# everything assuming 16kHz
SAMPLE_RATE = 16000
DUR_THRESH = 1.2

# two thresholds: delta (change in amp) and duration (shortest distinguishable is 1.2ms (Irwin & Purdy, 1982))
DELTA_THRESH = 4.0e-05
SAMPLE_COUNT_THRESH = (DUR_THRESH / 1000) * SAMPLE_RATE

sampleSoundObject <- function(sndObj) {
  l = length(sndObj@left)
  s1 <- sndObj@left
  s1 <- s1 / 2^(sndObj@bit -1)
  return(s1)  
}

dSamplesFromFile <- function(filename) {
  sample <-sampleSoundObject(readWave(filename))
  difs <- diff(sample)
  difs_difs <- diff(abs(difs))
  return (list(sample, abs(difs), abs(difs_difs))) # dubious 'abs'
}

files <- sapply(c(1,2,3), FUN=function(ihateR) {sprintf('local/nan-ai-file-%d.wav', ihateR)})
slices <- matrix(data=c(34891,35050,41740,42056,1,Inf), byrow = TRUE, nrow = 3, ncol = 2)
widenSliceBy <- function(slice, wid=3000) {
  return( c(max(0,slice[1]-wid), slice[2]+wid) )
}
slices <- t(apply(slices, 1, FUN=widenSliceBy))

test_data <- matrix(cbind(files, slices), ncol=3, nrow=3) # in a perfect world this wouldn't be necessary

