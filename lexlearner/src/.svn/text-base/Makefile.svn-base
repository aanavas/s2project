###########################################################################
##                                                                       ##
##                   Language Technologies Institute                     ##
##                     Carnegie Mellon University                        ##
##                       Copyright (c) 2005-2006                         ##
##                        All Rights Reserved.                           ##
##                                                                       ##
##  Permission is hereby granted, free of charge, to use and distribute  ##
##  this software and its documentation without restriction, including   ##
##  without limitation the rights to use, copy, modify, merge, publish,  ##
##  distribute, sublicense, and/or sell copies of this work, and to      ##
##  permit persons to whom this work is furnished to do so, subject to   ##
##  the following conditions:                                            ##
##   1. The code must retain the above copyright notice, this list of    ##
##      conditions and the following disclaimer.                         ##
##   2. Any modifications must be clearly marked as such.                ##
##   3. Original authors' names are not deleted.                         ##
##   4. The authors' names are not used to endorse or promote products   ##
##      derived from this software without specific prior written        ##
##      permission.                                                      ##
##                                                                       ##
##  CARNEGIE MELLON UNIVERSITY AND THE CONTRIBUTORS TO THIS WORK         ##
##  DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING      ##
##  ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT   ##
##  SHALL CARNEGIE MELLON UNIVERSITY NOR THE CONTRIBUTORS BE LIABLE      ##
##  FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES    ##
##  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN   ##
##  AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,          ##
##  ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF       ##
##  THIS SOFTWARE.                                                       ##
##                                                                       ##
###########################################################################
###                                                                      ##
###  Lexicon and LTS builder                                             ##
###                                                                      ##
###########################################################################
TOP=../..
DIRNAME=lexlearner/src
BUILD_DIRS=
ALL_DIRS= util scripts config $(BUILD_DIRS)
SCRIPTS= ConfigPath.py \
         DictionaryIO.py \
         DynamicTimeWarpExperimental.py \
         FestivalInterface.py \
         LTS_Allowables.py \
         LTS_IO.py \
         LTS_RuleLearner.py \
         LTS_RuleLearnerSrvr.py \
         SimpleWordSelector.py \
         get_words_from_server.py \
         measure_word_coverage.py \
         scan_for_lexlearners.py \
         tinytest_lts_learner.py \
         LTS_RuleSystem.py \
         LTS_RuleSystemTrain.py \
         LTS_WebInterface.py \
         LatinCharacterSet.py \
         PronunciationOracle.py \
         WordSelector.py \
         lts_learner_command.py \
         test_lts_learner.py

FILES = $(SCRIPTS) Makefile

ALL = $(BUILD_DIRS)

include $(TOP)/config/common_make_rules

