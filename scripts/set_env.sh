#!/usr/bin/env bash

# author: Yevgeniy Puzikov
# This file sets environment variables which are used in different scripts
# Affected lines in original code (previously hard-coded):

#depparser.py:        stanford_path = "/home/j/llc/cwang24/R_D/AMRParsing/stanfordnlp/stanford-parser/"
#stanfordnlp/corenlp.py:        corenlp_path = os.path.relpath(__file__).split('/')[0]+"/stanford-corenlp-full-2015-04-20/"
#scripts/cparse.sh:STANFORD_PATH="/home/j/llc/cwang24/R_D/AMRParsing/stanfordnlp/stanford-parser"
#scripts/jamr_align.sh:JAMR_HOME="/home/j/llc/cwang24/Tools/jamr"

# Set these paths before running anything!
# The scripts above are modified to take into account the paths you provide.

export CORENLP_PATH=$HOME/projects/amr/camr/stanfordnlp/stanford-corenlp-full-2015-04-20
export STANFORD_PARSER_PATH=$HOME/projects/amr/camr/stanfordnlp/stanford-parser-full-2014-01-04
export JAMR_HOME=$HOME/projects/amr/jamr

# There is one path variable which has to be changed depending on
# whether we run original AMR data or the one mapped from ISI-aligned data
export CORENLP_PROPERTIES_PATH=$HOME/projects/amr/camr/stanfordnlp/isi2jamr.properties

# for our experiments with mapping ISI alignments to JAMR alignments,
# this has to be changed to a different properties file
# the only property which has changed is: tokenize.whitespace=true
#export CORENLP_PROPERTIES_PATH=$HOME/projects/amr/camr/stanfordnlp/isi2jamr.properties

