reset

set term post color eps enh  "Times-Roman" 23 # size 10, 10
set output 'rho_i.eps' 
set key right top
#set yrange[0:700]
set pointsize 1
#set grid x
#set grid y

set xrange [1:20]
set xlabel "Class Id (i)"
set ylabel "{/Symbol r} "
plot 	'rho_i_lambda.dat' u ($1):($2) with linespoints title "{/Symbol l}=0.010, {/Symbol r}_{tilde}=0.08", \
		'rho_i_lambda.dat' u ($1):($3) with linespoints title "{/Symbol l}=0.022, {/Symbol r}_{tilde}=0.18", \
		'rho_i_lambda.dat' u ($1):($4) with linespoints title "{/Symbol l}=0.034, {/Symbol r}_{tilde}=0.27", \
		'rho_i_lambda.dat' u ($1):($5) with linespoints title "{/Symbol l}=0.046, {/Symbol r}_{tilde}=0.37", \
		'rho_i_lambda.dat' u ($1):($6) with linespoints title "{/Symbol l}=0.058, {/Symbol r}_{tilde}=0.47", \
		'rho_i_lambda.dat' u ($1):($7) with linespoints title "{/Symbol l}=0.070, {/Symbol r}_{tilde}=0.57", \
		'rho_i_lambda.dat' u ($1):($8) with linespoints title "{/Symbol l}=0.082, {/Symbol r}_{tilde}=0.67", \
		'rho_i_lambda.dat' u ($1):($9) with linespoints title "{/Symbol l}=0.094, {/Symbol r}_{tilde}=0.77", \
		'rho_i_lambda.dat' u ($1):($9) with linespoints title "{/Symbol l}=0.094, {/Symbol r}_{tilde}=0.77", \
		'rho_i_lambda.dat' u ($1):($10) with linespoints title "{/Symbol l}=0.106, {/Symbol r}_{tilde}=0.86", \
		'rho_i_lambda.dat' u ($1):($11) with linespoints title "{/Symbol l}=0.118, {/Symbol r}_{tilde}=0.96"

#set term post color eps enh  "Times-Roman" 23
#set key right top
#set xlabel "Class id (k)"
#set ylabel "Miss rate, {/Symbol m}^{f} [chunk/s]"
#set yrange[0:700]
#set pointsize 1.8
#set grid x
#set grid y
#set output "../eps/line/multiple_file_uniform_filtering_cache20000_alpha2_lambda20/line_miss_rate_multiple_uniform_file_filtering_cache20000_alpha2_lambda20.eps"

#!echo 'source("../../formula.r"); print_cascade_filtering("../../test_multiple_uniform_a1_7.dat",503.8,10,20000,2,20,1.7); ' | R --no-save


#plot '../../tests/line/multiple_file_uniform_filtering_cache20000_alpha1.7_lambda20/CACHE1.log' u ($10):($4) w lp lw 3 lc 0 lt 1 pt 4 notitle,\
#     '../../tests/line/multiple_file_uniform_filtering_cache20000_alpha2_lambda20/CACHE1.log' u ($10):($4) w lp lw 3 lc 0 lt 1 pt 6 notitle,\
#     '../../tests/line/multiple_file_uniform_filtering_cache20000_alpha2.3_lambda20/CACHE1.log' u ($10):($4) w lp lw 3 lc 0 lt 1 pt 8 notitle,\
#     '../../test_multiple_uniform_a1_7.dat.missrate' u ($1):($2) w lp lc 0 lw 3 lt 3 pt 4 notitle,\
#     '../../test_multiple_uniform_a2.dat.missrate' u ($1):($2) w lp lc 0 lw 3 lt 3 pt 6 notitle,\
#     '../../test_multiple_uniform_a2_3.dat.missrate' u ($1):($2) w lp lc 0 lw 3 lt 3 pt 8 notitle,\
#     -1 w p pt 4 lw 3 lc 0 title ' {/Symbol a} = 1.7 ',\
#     -1 w p pt 6 lw 3 lc 0 title ' {/Symbol a} = 2 ',\
#     -1 w p pt 8 lw 3 lc 0 title ' {/Symbol a} = 2.3 ',\
#     -1 w l lt 1 lw 3 lc 0 title ' Simulation ',\
#     -1 w l lt 3 lw 3 lc 0 title ' Model '

#!epstopdf --outfile=../../../documents/transport/fig/line_miss_rate_filtering.pdf ../eps/line/multiple_file_uniform_filtering_cache20000_alpha2_lambda20/line_miss_rate_multiple_uniform_file_filtering_cache20000_alpha2_lambda20.eps
