reset

set term post color eps enh  "Times-Roman" 23 # size 10, 10
set output 'pmiss.eps' 
set key right bottom
#set yrange[0:700]
set pointsize 1.5
#set grid x
#set grid y

set xrange [0:20]
set xlabel "Class Id (i)"
set ylabel "p_i"
plot 	'pmiss.exp' u ($1) with linespoints  lw 2 title "Experimental", \
		'pmiss.dat' u ($2) with linespoints  lw 2 title "Theoretical"
