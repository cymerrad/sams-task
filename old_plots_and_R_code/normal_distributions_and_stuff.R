library("dplyr")
library("ggpubr")
library("ggplot2")

sample3 <- lotsofdata[[3]][[1]]
sample2 <- lotsofdata[[2]][[1]]
sample1 <- lotsofdata[[1]][[1]]

# alright, so I will be using Kolmogorov-Smirnov for comparing "silence" from beggining or end of the tracks to drops in amplitude

timeArray <- (0:(length(sample1)-1))
SILENCE_THRESHOLD = 1e-02
below_thr_bool <- (function(x) abs(x)<SILENCE_THRESHOLD )(sample1)

MAGICAL_CONSTANT = 30

pdf("signals_with_silence_threshold.pdf")
lapply(list(sample1, sample2, sample3), FUN=function(SAMPLE){ 
  timeArray <- (0:(length(SAMPLE)-1))
  below_thr_bool <- (function(x) abs(x)<SILENCE_THRESHOLD )(SAMPLE)
  below_thr_rle <- rle(below_thr_bool)
  n_rle_values <- mapply(function(X, Y) { if(X > MAGICAL_CONSTANT && Y) return(TRUE) else return(FALSE) }, X=below_thr_rle$lengths, Y=below_thr_rle$values)
  n_rle <- below_thr_rle
  n_rle$values <- n_rle_values
  new_below <- inverse.rle(n_rle)
  n_rle_again_lol <-rle(new_below)
  g <- ggplot(data=NULL, mapping = aes(timeArray)) +
    geom_line(aes(y=SAMPLE), colour="red", alpha=0.4)
  g + geom_ribbon(aes(ymin=-0.01 * below_thr_bool, ymax=0.01 * new_below), alpha=0.3, fill="yellow")
})

dev.off()

g <- ggplot(data=NULL, mapping = aes(timeArray)) +
  geom_line(aes(y=sample1), colour="red", alpha=0.4)

g_ribbon <- g + geom_ribbon(aes(ymin=-0.01 * below_thr_bool, ymax=0.01 * below_thr_bool), alpha=0.3, fill="yellow")

below_thr_rle <- rle(below_thr_bool)
sample1_silence_pre <-sample1[1:head(below_thr_rle$lengths, n=1)]
sample1_silence_post <- sample1[ (length(sample1)-tail(below_thr_rle$lengths, n=1)):(length(sample1)) ]

# these two have roughly the same distribution
ggdensity(sample1_silence_pre)
ggdensity(sample1_silence_post)

# from this stems my main assumption: every other silence inside has also the same distribution
n_rle_values <- mapply(function(X, Y) { if(X > MAGICAL_CONSTANT && Y) return(TRUE) else return(FALSE) }, X=below_thr_rle$lengths, Y=below_thr_rle$values)
n_rle <- below_thr_rle
n_rle$values <- n_rle_values
new_below <- inverse.rle(n_rle)
n_rle_again_lol <-rle(new_below)

g_ribbon2 <- g + geom_ribbon(aes(ymin=-0.01 * new_below, ymax=0.01 * new_below), alpha=0.3, fill="yellow")

rand_range_from_ofsize <- function(l,r,size) {
  if (size > r-l) return(c(0,0)) # should be some error, but I can't be bovvered
  
  left <- floor(runif(1,l,r-size+1))
  right <- left + size -1 
  return(c(left,right))
}

# from our newest rle create ranges of 'quiet' zones

state <<- head(n_rle_again_lol$values, n=1) # should be TRUE
cur <<- 0
lefties <- c()
righties <- c()
for (x in n_rle_again_lol$lengths) {
  if (state) {
    lefties <- append(lefties, cur)
    righties <- append(righties, cur+x)
  }
  state <- !state
  cur <- cur + x
}
ranges <- cbind(lefties, righties)
attr(ranges, "dimnames") <- NULL # another unecessary line BECAUSE R SUCKS

apply(ranges[c(-1,-nrow(ranges)),], 1, FUN=function(x) {
  rr <- rand_range_from_ofsize(0, 10000, x[2] - x[1] + 1)
  cat(sprintf("Attempting [%d:%d] (len %d) with [%d:%d] (len %d)\n", x[1], x[2], (x[2] - x[1] + 1), rr[1], rr[2], (rr[2] - rr[1] +1)))
  if (!is.null(x)) {
    ks.test(sample1[x[1]:x[2]], sample1[rr[1]:rr[2]])
  }
})

zoom_to_row <- function(row) {
  return(xlim(row[1], row[2]))
}
