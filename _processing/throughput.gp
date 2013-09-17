reset

set term post eps enh  "Times-Roman" 23 # size 10, 10
set output 'throughput.eps' 
set key right top
#set yrange[0:700]
set pointsize 1.2
#set grid x
#set grid y
#set xtics ("1" 1, "2" 2, "4" 4, "6" 6, "8" 8, "10" 10, "12" 12, "14" 14, "16" 16, "18" 18, "20" 20)
set xtics ("1" 1, "3" 3, "5" 5, "7" 7, "9" 9, "11" 11, "13" 13, "15" 15, "17" 17, "19" 19)
set mxtics 2
set ytics 2

#set title "Theoretical and Experimental Throughput"
set xrange [1:20]
set xlabel "Class id (i)"
set ylabel "Throughput [Mbps]"
plot 'thr.dat' u ($1):($2 * 1e-6) with linespoints lt 1 pt 4 lw 2 title 'Theoretical', 'gp.exp' u ($1):($2 * 2 * 1e-6) with linespoints lt 3 pt 8 lw 2 title 'Experimental'
