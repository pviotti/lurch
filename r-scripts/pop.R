suppressMessages(library("VGAM"))

param_zipf = 2.0	# zipf parameter
n_files = 50		# number of files
n_req = 1000 		# number of requests (downloads) 

ps = dzipf(1:n_files, n_files, param_zipf)
req = sample(1:n_files, n_req, replace='TRUE', prob=ps)

#H = hist(req, breaks=1:(n_files+1)-0.5, prob=T)
#lines(1:n_files, ps)
#sum(H$density)
