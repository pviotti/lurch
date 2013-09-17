#!/usr/bin/python
# converts the first column from absolute to relative time 
# (seconds since the beginning of the experiment)

import sys
lines = sys.stdin.readlines()

start = float(lines[0].split(',')[0])

lines[0] = lines[0].replace(lines[0].split(",")[0], "0")
for l in lines[1:]:
	lines[lines.index(l)] = l.replace(l.split(",")[0], str(float(l.split(",")[0]) - start))

for l in lines:
	sys.stdout.write(l)
