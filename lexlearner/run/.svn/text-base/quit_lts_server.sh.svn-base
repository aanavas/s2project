#!/bin/sh
#
# quit_lts_server.sh
# ==================
# 0.001  10-Sep-2007  jmk  Created
# Comment: to identify ports with attached lexlearners, run scan_for_lexlearners.py

if [ "$#" == "0" ]
then
   echo "USAGE: quit_lts_server.sh port_number"
   exit
else
   python ../src/tinytest_lts_learner.py --port $1 --shutdown
fi

