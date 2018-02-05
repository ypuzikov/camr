#!/usr/bin/env bash

# author: Yevgeniy Puzikov
# This file sets environment variables which are used in different scripts
# Affected scripts (previously hard-coded paths):

#depparser.py:        stanford_path = "/home/j/llc/cwang24/R_D/AMRParsing/stanfordnlp/stanford-parser/"
#depparser.py:        clear_path="/home/j/llc/cwang24/Tools/clearnlp"
#depparser.py:        turbo_path="/home/j/llc/cwang24/Tools/TurboParser"
#depparser.py:        mate_path="/home/j/llc/cwang24/Tools/MateParser"
#scripts/stdconvert.sh:#CORENLP_PATH='/home/j/llc/cwang24/Tools/CoreNLP-mod-convert.jar'
#scripts/stdconvert.sh:#CORENLP_PATH='/home/j/llc/cwang24/Tools/CoreNLP-mod-convert-collapse.jar'
#scripts/cparse.sh:STANFORD_PATH="/home/j/llc/cwang24/R_D/AMRParsing/stanfordnlp/stanford-parser"
#scripts/create_prp_xml.sh:CORENLP_PATH="/home/j/llc/cwang24/Tools/stanford-corenlp-full-2015-04-20"
#scripts/jamr_align.sh:JAMR_HOME="/home/j/llc/cwang24/Tools/jamr"

# Set these paths before running anything!
# The scripts above are modified to take into account the paths you provide
CORENLP_PATH='$HOME/projects/camr/stanfordnlp/stanford-corenlp-full-2013-06-20'
STANFORD_PATH='$HOME/projects/camr/stanfordnlp/stanford-parser-full-2014-01-04'
JAMR_HOME='$HOME/projects/jamr'
CLEAR_PATH=''
MATE_PATH=''