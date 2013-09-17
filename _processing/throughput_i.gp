reset

set term post color eps enh  "Times-Roman" 23 # size 10, 10
set output 'throughput_i.eps' 
set key right top
#set yrange[0:700]
set pointsize 1
#set grid x
#set grid y

set xrange [1:20]
set xlabel "Class Id (i)"
set ylabel "Throughput [Mbps]"
plot 	'thr_i_lambda.dat' u ($1):($2 * 1e-6) with linespoints title "{/Symbol l}=0.03, {/Symbol r}=0.08", \
		'thr_i_lambda.dat' u ($1):($3 * 1e-6) with linespoints title "{/Symbol l}=0.06, {/Symbol r}=0.16", \
		'thr_i_lambda.dat' u ($1):($4 * 1e-6) with linespoints title "{/Symbol l}=0.09, {/Symbol r}=0.25", \
		'thr_i_lambda.dat' u ($1):($5 * 1e-6) with linespoints title "{/Symbol l}=0.13, {/Symbol r}=0.33", \
		'thr_i_lambda.dat' u ($1):($6 * 1e-6) with linespoints title "{/Symbol l}=0.16, {/Symbol r}=0.42", \
		'thr_i_lambda.dat' u ($1):($7 * 1e-6) with linespoints title "{/Symbol l}=0.19, {/Symbol r}=0.50", \
		'thr_i_lambda.dat' u ($1):($8 * 1e-6) with linespoints title "{/Symbol l}=0.22, {/Symbol r}=0.59", \
		'thr_i_lambda.dat' u ($1):($9 * 1e-6) with linespoints title "{/Symbol l}=0.25, {/Symbol r}=0.68", \
		'thr_i_lambda.dat' u ($1):($10 * 1e-6) with linespoints title "{/Symbol l}=0.29, {/Symbol r}=0.76", \
        'thr_i_lambda.dat' u ($1):($11 * 1e-6) with linespoints title "{/Symbol l}=0.31, {/Symbol r}=0.85"
