#!/bin/bash

mkdir graphs
mkdir _dat

# =================== NUMBER OF DOWNLOADS
cat lurch.log | python convert_time.py | awk -F, '{print $1 $NF}' > _dat/num_dw.dat

# =================== GOODPUT
cat lurch.log | python convert_time.py | grep Completed | awk -F, '{print $1 $4 }' > _dat/goodput.dat

# =================== RTTe
cat lurch.log | python convert_time.py | grep Completed | awk -F, '{print $1 $6 }' > _dat/rtte.dat

# =================== All-in-one graph of num. of downloads, goodput and RTTe
gnuplot  <<EOIN
reset

set terminal post eps enh "Times-Roman" 24 size 10, 10
set output './graphs/downloads.eps' 
unset key
set size 1.0, 1.0
set origin 0.0, 0.0
set multiplot

set size 1.0,0.33
set origin 0.0,0.66
set title "Number of Downloads"
set xlabel "Time [s]"
set ylabel "# Downloads"
plot "_dat/num_dw.dat" with steps

set size 1.0,0.33
set origin 0.0,0.33
set title "Goodput"
set xlabel "Time [s]"
set ylabel "Goodput [bps]"
plot "_dat/goodput.dat" with impulses

set size 1.0,0.33
set origin 0.0,0.0
set title "E[RTT]"
set xlabel "Time [s]"
set ylabel "E[RTT] [{/Symbol m}s]"
plot "_dat/rtte.dat" with impulses

unset multiplot
EOIN


# =================== POP

# FOR SINGLE FILES
# paste <(seq 1 50) <(cat pop_prob) | tr -s " " > pop_prob1; mv pop_prob1 pop_prob # TEMP generate prob distribution data
tot_dw=$(cat results.in | awk '{print $2}' | sed 's/NP/0/' | sed 's/NP_err/0/' | awk '{total+=$1; count+=1} END {print total}') # compute tot downloads
paste <(seq 1 50) <(cat results.in | awk '{print $2}' | sed 's/NP/0/' | sed 's/NP_err/0/' | awk -v tot="$tot_dw" '{print $1/tot}' ) | tr -s " " > _dat/rel_freq.dat

paste <(seq 1 50) <(cat results.in | tr -s " " | awk '{print $4}' | sed 's/^[ ]//') | sed '/^[0-9]*[ \t]*$/d' > _dat/pop_gp.dat
paste <(seq 1 50) <(cat results.in | tr -s " " | awk '{print $5}' | sed 's/^[ ]//') | sed '/^[0-9]*[ \t]*$/d' > _dat/pop_rtt.dat

gnuplot  <<EOIN
reset

set terminal post eps enh "Times-Roman" 24 size 10, 10
set output './graphs/pop.eps' 
unset key
set size 0.9, 1.62
set origin 0.0, 0.0
set multiplot

set size 0.9,0.54
set origin 0.0,1.08
set title "Popularity (distribution and real frequencies)"
set xlabel "Files"
#set ylabel "# Downloads"
set xrange [:10]
plot "pop_prob.in" with lines, "_dat/rel_freq.dat" with histeps

set size 0.9,0.54
set origin 0.0,0.54
set xrange [:10]
set title "Goodput"
set xlabel "Files"
set ylabel "Goodput [bps]"
plot "_dat/pop_gp.dat" with lines, "_dat/pop_gp.dat" with points

set size 0.9,0.54
set origin 0.0,0.0
set xrange [:10]
set title "RTT"
set xlabel "Files"
set ylabel "E[RTT] [{/Symbol m}s]"
plot "_dat/pop_rtt.dat" with lines, "_dat/pop_rtt.dat" with points

unset multiplot
EOIN

# FOR FREQUENCY CLASSES
tot_downloads=$(cat results.in | awk '{total+=$2; count+=1} END {print total}')
cat results.in | tr -s " " | awk -v tot="$tot_downloads" '{if (NF>2) print $2, $4}' | sed 's/^[ ]//' | python mean.py | sort -n > _dat/pop_class_gp.dat
cat results.in | tr -s " " | awk -v tot="$tot_downloads" '{if (NF>2) print $2, $5}' | sed 's/^[ ]//' | python mean.py | sort -n > _dat/pop_class_rtt.dat

gnuplot  <<EOIN
reset

set terminal post eps enh "Times-Roman" 24 size 10, 10
set output './graphs/pop_classes.eps' 
unset key
set size 1.0, 1.0
set origin 0.0, 0.0
set multiplot

set size 1.0,0.5
set origin 0.0,0.5
#set title "Number of Downloads"
set xlabel "Popularity Classes [# of downloads]"
set ylabel "Goodput [bps]"
plot "_dat/pop_class_gp.dat" with lines, "_dat/pop_class_gp.dat" with points

set size 1.0,0.5
set origin 0.0,0.0
#set title "Goodput"
set xlabel "Popularity Classes [# of downloads]"
set ylabel "E[RTT] [{/Symbol m}s]"
plot "_dat/pop_class_rtt.dat" with lines, "_dat/pop_class_rtt.dat" with points

unset multiplot
EOIN


# =================== DELAY
#cat delay.log | python analise_delay.py 2> delay_stats.info | awk '{print $1, $2}' > _dat/delay.dat 

#gnuplot  <<EOIN
#reset

#set terminal post eps enh "Times-Roman" 24 size 10, 8
#set output './graphs/delay.eps' 
#unset key
#set size 1.0, 1.0

#set title "Delay of video packets"
#set ylabel "Delay [s]"
#set xlabel "Chunk ID"
#plot "_dat/delay.dat" with points

#EOIN
