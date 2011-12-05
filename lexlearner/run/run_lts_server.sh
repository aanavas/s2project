#!/bin/sh

# Purpose:
#   The shell script setvars_exec.sh sets environment variables
#   needed by Festival and friends, and then invokes the following
#   command (running the lexlearner server).
# Example:
#   ./run_lts_server.sh --port 8000 --festdict ../dicts/pron-dict.us_english_4k.scm

EXEC=../../bin/setvars_exec.sh
$EXEC python ../src/LTS_RuleLearnerSrvr.py $*

# $EXEC py ../src/LTS_RuleLearnerSrvr.py $*
