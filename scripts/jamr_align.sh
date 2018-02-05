#!/bin/bash

source ./set_env.sh

#### Config ####
${JAMR_HOME}/scripts/config.sh

#### Align the tokenized amr file ####

echo "### Aligning $1 ###"
# input should be tokenized AMR file, which has :tok tag in the comments
${JAMR_HOME}/run Aligner -v 0 < $1 > $1.aligned