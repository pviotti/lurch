suppressMessages(library("VGAM"))

file_size = 42e6 #8e7 		# 5 MB (expressed in bit)
N = 5				# mean number of clients in the queue
C = 1e7				# 10 Mbps, the bottleneck
h = 0.3				# Overhead (due to headers: 768 byte of app-level content in a MTU sized packet, 1500 bytes)
num_intervals =1000.0	# number of requests

# Mean request rate
# computed using Little's Law for a M/G/1-PS system
#lambda = ( N * C ) / ( ( 1 + h ) * file_size * (N + 1) )
lambda = 0.19 #0.045
#lambda = 0.19
interval_avg = 1 / lambda

ps = dpois(1:num_intervals, interval_avg)
intervals = sample(1.0:num_intervals, num_intervals, replace='TRUE', prob=ps)

#hist(intervals, breaks=1:(30)-0.5, prob=T)
#lines(1:num_intervals, ps)
