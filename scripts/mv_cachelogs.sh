#!/bin/bash

mkdir -p ./cache_logs

#scp cuenca:/home/viotti/ccnd_cache.log ./cache_logs/cuenca_cache.log
#scp bird:/home/viotti/ccnd_cache.log ./cache_logs/bird_cache.log
scp p-impact:/home/viotti/ccnd_cache.log ./cache_logs/p-impact_cache.log
mv /home/viotti/ccnd_cache.log ./cache_logs/bird_cache.log
