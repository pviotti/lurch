#!/usr/bin/env python
# given n files of data about goodput (on the second column)
# compute the avg values and write it on a file

import os

num_files = 6
num_val = 20

goodput_file_name = "pop_gp_{0}.dat"
output_file = "gp.exp"

res = []

for i in range(0, num_files):
	lines = open(goodput_file_name.format(str(i))).readlines()
	for k in range(0, num_val):
		if len(res) >= k+1:
			res[k] += float(lines[k].split()[1])
		else:
			res.append(float(lines[k].split()[1]))

f = open(output_file, 'w')		
for i in range(0, num_val):
	res[i] = res[i] / num_files
	#print res[i]
	f.write(str(i + 1) + " " + str(res[i])+'\n')
f.close()

# ======================
# pmiss average, same as above

#goodput_file_name = "first_{0}.dat"
#output_file = "pmiss.exp"

#res = []

#for i in range(0, num_files):
	#lines = open(goodput_file_name.format(str(i))).readlines()
	#for k in range(0, num_val):
		#if len(res) >= k+1:
			#res[k] += float(lines[k])
		#else:
			#res.append(float(lines[k]))

#f = open(output_file, 'w')		
#for i in range(0, num_val):
	#res[i] = res[i] / num_files
	##print res[i]
	#f.write(str(res[i])+'\n')
#f.close()
