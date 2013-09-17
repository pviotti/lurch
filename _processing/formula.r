# ex:
# source('formula.r')
# print_all(2.0, 0.19, 6827, 34150, 1e7)

print_all<-function(alpha, lambda, sigma, CS, capacity) {
	suppressMessages(library(VGAM));
	
	# ====== PREDEFINED PARAMETERS: (temp)
	alpha = 2.0
	lambda = 0.19
	sigma = 6827
	CS = 34150
	capacity = 4.8e6
	
	printed_classes=20;
	n = 50;							# number of classes
	file_size = sigma * 1500 * 8;	# [bit]
	
	# q
	q_i = dzipf(1:n, n, alpha)
	#write.table(as.table(cbind(c(1:printed_classes), q_i[1:printed_classes])), file="q.dat",row.name=FALSE,col.name=FALSE);	
	
	# ======== P_MISS SPERIMENTALE (temp)
	#data = read.table('./pmiss.exp', header=FALSE, col.name="pmiss_exp")	# LEGGE DA FILE LA P_MISS DELL'ESPERIMENTO
	#attach(data)															# E LA METTE IN "pmiss_exp"
	
	# pmiss
	i=seq(1,n);
	K = sum(1/(i^alpha)) / ((gamma(1-1/alpha))^alpha);
	pmiss_i = exp(-K * q_i * (CS / sigma)^alpha);
	#write.table(as.table(cbind(c(1:printed_classes), pmiss_i[1:printed_classes])), file="pmiss.dat",row.name=FALSE,col.name=FALSE);	

	# lambda
	lambda_i = q_i * lambda
	#write.table(as.table(cbind(c(1:printed_classes), lambda_i[1:printed_classes])), file="lambda.dat",row.name=FALSE,col.name=FALSE);	

	# rho
	rho_tilde = lambda * file_size / capacity; # rho without caching
	rho_i = pmiss_i  * q_i * rho_tilde;
	#rho_i = pmiss_exp * q_i * rho_tilde;		# RHO CALCOLATO CON LA P_MISS DELL'ESPERIMENTO
	#write.table(as.table(cbind(c(1:printed_classes), rho_i[1:printed_classes])), file="rho.dat",row.name=FALSE,col.name=FALSE);	
	
	# throughput
	Thr_local = 17e6 		# [bps] throughput of files retrieved from local cache (Goodput * 2) -- it is 38.8 Mbps
    Thr_i = (capacity * (1 - sum(rho_i)) * Thr_local) / ( Thr_local * pmiss_i + (1 - sum(rho_i)) * capacity * (1 - pmiss_i) )
	#Thr_i = (capacity * (1 - sum(rho_i)) * Thr_local) / ( Thr_local * pmiss_exp + (1 - sum(rho_i)) * capacity * (1 - pmiss_exp) ) # by Luca 9/8/2010, -- CON LA P_MISS DELL'ESPERIMENTO
	write.table(as.table(cbind(c(1:printed_classes), Thr_i[1:printed_classes])), file="thr.dat",row.name=FALSE,col.name=FALSE);	
    
}

print_rho<-function(alpha, sigma, cache_size, capacity) {
	suppressMessages(library(VGAM));
	
    # ====== PREDEFINED PARAMETERS: (temp)
	alpha = 2.0
	sigma = 6827
	CS = 34150
	capacity = 5e6
	
	printed_classes=20;
	n = 50;							# number of classes
	file_size = sigma * 1500 * 8;	# [bit]
    
    # q
	q_i = dzipf(1:n, n, alpha)

	# pmiss
	i=seq(1,n);
	K = sum(1/(i^alpha)) / ((gamma(1-1/alpha))^alpha);
	pmiss_i = exp(-K * q_i * (CS / sigma)^alpha);
	
	rho_i_matr = 0
	for ( lambda in seq(0.03, 0.34, 0.032)) { # for 0 < rho < 1
		# lambda
		lambda_i = q_i * lambda

		# rho
		rho_tilde = lambda * file_size / capacity; # rho without caching
		rho_i = pmiss_i[1:printed_classes] * q_i[1:printed_classes] * rho_tilde;
		#print(lambda)
        #print(rho_tilde)
        #print(sum(rho_i))
		if (length(rho_i_matr)==1)
			rho_i_matr = rho_i
		else
			rho_i_matr = cbind(rho_i_matr, rho_i)

	}
	#print(rho_i_matr)
	write.table(as.table(cbind(c(1:printed_classes), rho_i_matr)), file="rho_i_lambda.dat",row.name=FALSE,col.name=FALSE);	
}


print_throughput<-function(alpha, sigma, cache_size, capacity) {
	suppressMessages(library(VGAM));
	
    # ====== PREDEFINED PARAMETERS: (temp)
	alpha = 2.0
	sigma = 6827
	CS = 34150
	capacity = 5e6
	
	printed_classes=20;
	n = 50;							# number of classes
	file_size = sigma * 1500 * 8;	# [bit]
    
    # q
	q_i = dzipf(1:n, n, alpha)

	# pmiss
	i=seq(1,n);
	K = sum(1/(i^alpha)) / ((gamma(1-1/alpha))^alpha);
	pmiss_i = exp(-K * q_i * (CS / sigma)^alpha);
	
	
	Thr_i_matr = 0
	Thr_local = 20e6 		# [bps] throughput of files retrieved from local cache (Goodput * 2)
	for ( lambda in seq(0.03, 0.34, 0.032)) { # for 0 < rho < 1
		# lambda
		lambda_i = q_i * lambda

		# rho
		rho_tilde = lambda * file_size / capacity; # rho without caching
		rho_i = pmiss_i * q_i * rho_tilde;
		
		# throughput
        Thr_i = (capacity * (1 - sum(rho_i)) * Thr_local) / ( Thr_local * pmiss_i + (1 - sum(rho_i)) * capacity * (1 - pmiss_i) )
        #print(rho_tilde)
		#print(rho_i)
		if (length(Thr_i_matr)==1)
			Thr_i_matr = Thr_i[1:printed_classes]
		else
			Thr_i_matr = cbind(Thr_i_matr, Thr_i[1:printed_classes])
	}
	#print(Thr_i_matr)
	write.table(as.table(cbind(c(1:printed_classes), Thr_i_matr)), file="thr_i_lambda.dat",row.name=FALSE,col.name=FALSE);	
}
