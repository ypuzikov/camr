#!/usr/bin/env bash

# author: Yevgeniy Puzikov
# This file sets environment variables which are used in different scripts
# Affected lines in original code (previously hard-coded):

#depparser.py:        stanford_path = "/home/j/llc/cwang24/R_D/AMRParsing/stanfordnlp/stanford-parser/"
#scripts/cparse.sh:STANFORD_PATH="/home/j/llc/cwang24/R_D/AMRParsing/stanfordnlp/stanford-parser"
#scripts/jamr_align.sh:JAMR_HOME="/home/j/llc/cwang24/Tools/jamr"

# Set these paths before running anything!
# The scripts above are modified to take into account the paths you provide.

CORENLP_PATH='$HOME/projects/camr/stanfordnlp/stanford-corenlp-full-2013-06-20'
STANFORD_PARSER_PATH='$HOME/projects/camr/stanfordnlp/stanford-parser-full-2014-01-04'
JAMR_HOME='$HOME/projects/jamr'
