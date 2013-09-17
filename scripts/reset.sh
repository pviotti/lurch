#!/bin/bash

ccndstop
rm ccnd_cache.log
export CCND_CAP=34150 # 20490 = 3, 27330 = 4 Files of 5 MB, with 768 B per chunk
export CCND_DATA_PAUSE_MICROSEC=1000 # content-send delay time for multicast and uplink faces
export CCND_DEBUG=0
ccndstart 
bash *_ccnrouting.sh
