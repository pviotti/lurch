#!/usr/bin/python
# computes the mean value over the second column values
# for every different value of the first

import sys
lines = sys.stdin.readlines()

di = {}
for l in lines:
	if l.split()[0] not in di.keys():
		di[l.split()[0]] = [ l.split()[1] ]
	else:
		di[l.split()[0]].append(l.split()[1])

for k in di.keys():
	sum = 0
	for v in di[k]:
		sum += float(v)
	ln = len(di[k])
	di[k] = sum / ln
	


for k in di.keys():
	sys.stdout.write(k)
	sys.stdout.write(" ")
	sys.stdout.write(str(di[k]))
	sys.stdout.write("\n")
