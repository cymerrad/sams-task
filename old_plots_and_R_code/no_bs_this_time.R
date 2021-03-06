library(tuneR)
library(ggplot2)

# everything assuming 16kHz
SAMPLE_RATE = 16000
DUR_THRESH = 1.2

# two thresholds: delta (change in amp) and duration (shortest distinguishable is 1.2ms (Irwin & Purdy, 1982))
DELTA_THRESH = 1e-04
SAMPLE_COUNT_THRESH = (DUR_THRESH / 1000) * SAMPLE_RATE

# one more for differentiating between signal and silence
STATIC_THRESH = 5e-05

sampleSoundObject <- function(sndObj) {
  l = length(sndObj@left)
  s1 <- sndObj@left
  s1 <- s1 / 2^(sndObj@bit -1)
  return(s1)  
}

dSamplesFromFile <- function(filename) {
  sample <-sampleSoundObject(readWave(filename))
  difs <- diff(sample)
  difs_difs <- diff(difs)
  return (list(sample, difs, difs_difs)) # dubious 'abs'
}

files <- sapply(c(1,2,3), FUN=function(ihateR) {sprintf('local/nan-ai-file-%d.wav', ihateR)})
slices <- matrix(data=c(34891,35050,41740,42056,1,Inf), byrow = TRUE, nrow = 3, ncol = 2)
widenSliceBy <- function(slice, wid=3000) {
  return( c(max(0,slice[1]-wid), slice[2]+wid) )
}
slices <- t(apply(slices, 1, FUN=widenSliceBy))

test_data <- matrix(cbind(files, slices), ncol=3, nrow=3) # in a perfect world this wouldn't be necessary


lotsofdata <- apply(test_data, 1, FUN=function(x) {
  dSamplesFromFile(filename = x[1])
})

data1 <- lotsofdata[[1]][[1]]
data2 <- lotsofdata[[1]][[2]]
data3 <- lotsofdata[[1]][[3]]

overlapHists <- function(data1, data2, data3=NULL, l=1, r=Inf, main='') {
  biggerLen <- max(length(data1), length(data2), length(data3))
  length(data1) <- biggerLen # WHY IS IT EVEN POSSIBLE
  length(data2) <- biggerLen
  
  if (!is.null(data3)) {
    length(data3) <- biggerLen
  }
  
  r <- min(r, biggerLen)
  
  xx <- (0:(biggerLen-1))
  
  g <- ggplot(data=NULL, mapping=aes(xx)) +            
    geom_line(aes(y=data1), colour="red", alpha=0.4) + 
    geom_line(aes(y=data2), colour="green", alpha=0.4) +
    xlim(l,r)
  
  if (!is.null(data3)) {
    g <- g + geom_line(aes(y=data3), colour="blue", alpha=0.4)
  }
  
  # flats <- suppTresh(data1, abs(data2))
  # g <- g + geom_line(aes(y=flats[l:r]), colour="purple")
  # g_a <- g + annotate("rect", xmin=34891, xmax=35050, ymin=-Inf, ymax=Inf, alpha=.2, fill="yellow")
  
  g
}

suppTresh <- function(data1, data2, delta_tresh=DELTA_THRESH, count_tresh=SAMPLE_COUNT_THRESH, static_tresh=STATIC_THRESH) {
  # above <- (function(x) x > delta_tresh)(data2)
  above <- mapply(function(X,Y) { (X>static_tresh) || (Y>delta_tresh) }, X=data1, Y=data2 )
  above_rle <- rle(above)
  above_rle$values = mapply(function(X,Y){ if(X>count_tresh) return(Y) else return(FALSE) }, X=above_rle$lengths, Y=above_rle$values)
  above <- inverse.rle(above_rle)
  as.integer(above)
}

# pdf("plots6.pdf")
# 
# lapply(lotsofdata, FUN=function(x){ overlapHists( abs( x[[1]] ), abs( x[[2]] ), abs( x[[3]] ) ) })
# 
# dev.off()



