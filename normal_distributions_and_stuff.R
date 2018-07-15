library("dplyr")
library("ggpubr")
library("ggplot2")

sample1 <- lotsofdata[[1]][[1]]
sample2 <- lotsofdata[[2]][[1]]
sample3 <- lotsofdata[[3]][[1]]

length(sample2) = length(sample1)
length(sample3) = length(sample1)
df <- data.frame(sample1, sample2, sample3)

# alright, so I will be using Kolmogorov-Smirnov for comparing "silence" from beggining or end of the tracks to drops in amplitude

timeArray <- (0:(length(sample1)-1))
SILENCE_THRESHOLD = 5e-04
below_thr_bool <- (function(x) abs(x)<SILENCE_THRESHOLD )(sample1)

g <- ggplot(data=NULL, mapping = aes(timeArray)) +
  geom_line(aes(y=sample1), colour="red", alpha=0.4) +
  geom_ribbon(aes(ymin=-0.01 * below_thr_bool, ymax=0.01 * below_thr_bool), alpha=0.3, fill="yellow")

below_thr_rle <- rle(below_thr_bool)
sample1_silence_pre <-sample1[1:head(below_thr_rle$lengths, n=1)]
sample1_silence_post <- sample1[ (length(sample1)-tail(below_thr_rle$lengths, n=1)):(length(sample1)) ]

# these two have roughly the same distribution
ggdensity(sample1_silence_pre)
ggdensity(sample1_silence_post)

# from this stems my main assumption: every other silence in has also the same distribution