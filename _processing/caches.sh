#!/bin/bash
# analise the chache logs

# grep -v ccnx:/ccnx/ : to grep out the chunks about key exchange, "pings", and metadata
# scale=2 :  floating point precision in bc

# bird
tot_bird=$(cat bird_cache.log | grep -v ccnx:/ccnx/ | wc -l)
matched_bird=$(cat bird_cache.log | grep -v ccnx:/ccnx/ | grep Matched | wc -l)
unmatched_bird=$(cat bird_cache.log | grep -v ccnx:/ccnx/ | grep Unmatched | wc -l)

#echo "On bird:"
#echo "Tot: $tot_bird, Matched: $matched_bird, Unmatched: $unmatched_bird"
#echo

# p-impact
tot_impact=$(cat p-impact_cache.log | grep -v ccnx:/ccnx/ | wc -l)
matched_impact=$(cat p-impact_cache.log | grep -v ccnx:/ccnx/ | grep Matched | wc -l)
unmatched_impact=$(cat p-impact_cache.log | grep -v ccnx:/ccnx/ | grep Unmatched | wc -l)

#echo "On impact:"
#echo "Tot: $tot_impact, Matched: $matched_impact, Unmatched: $unmatched_impact"
#echo "Matched percentage: $(echo "scale=2; $matched_impact * 100 / $tot_impact" | bc -l) %"
#echo

echo "Hit percentage on first cache: $(echo "scale=2; $matched_bird * 100 / $tot_bird" | bc -l) %"
echo "Hit percentage on second cache: $(echo "scale=2; $matched_impact * 100 / $tot_bird" | bc -l) %"
echo "Hit percentage on source: $(echo "scale=2; $unmatched_impact * 100 / $tot_bird" | bc -l) %"

# NB:
# The total does not reach the 100%. Maybe beacause some interest at the consumer (first cache) are due to 
# timeouts and are not propagated by ccnd.


echo
from_cuenca=$(cat bird_cache.log | grep -v ccnx:/ccnx/ | grep cuenca | wc -l)
from_laptop=$(cat bird_cache.log | grep -v ccnx:/ccnx/ | grep zebra | wc -l)
echo "From cuenca: $from_cuenca, $(echo "scale=2; $from_cuenca * 100 / $tot_bird" | bc -l) %"
echo "From zebra: $from_laptop, $(echo "scale=2; $from_laptop * 100 / $tot_bird" | bc -l) %"



#cat bird_cache.log | grep -v ccnx:/ccnx/ | awk '{print $2, $4}' | sort -t " " -k 2,2 | uniq -dc

# default caching policy: drop packet arrived first

# cat results | tr -s " " | awk -F- '{if (min=="") {min=max=$2}; if($2>max) {max=$2}; if($2< min) {min=$2}; total+=$2; count+=1} END {print total/count, min, max}’
