#!/bin/bash

# Versions of the Stanford tools used
CORENLP_DIR="stanford-corenlp-full-2015-04-20"
STANFORD_PARSER_DIR="stanford-parser-full-2014-01-04"

# Smatch scoring script URL
SMATCH_URL="http://alt.qcri.org/semeval2016/task8/data/uploads/smatch-v2.0.2.tar.gz"

# 1. Get CoreNLP
echo "Setup Stanford CoreNLP ..."
cd stanfordnlp

if [ ! -d "$CORENLP_DIR" ]; then
    wget http://nlp.stanford.edu/software/$CORENLP_DIR.zip
    unzip stanford-corenlp-full-2015-04-20.zip
fi

if [ ! -d "$STANFORD_PARSER_DIR" ]; then
    wget http://nlp.stanford.edu/software/$STANFORD_PARSER_DIR.zip
    unzip stanford-parser-full-2014-01-04.zip
fi

# 2. Get Charniak Parser
echo "Setup Charniak Parser ..."
pip install --user bllipparser

# 3. Get Smatch scoring script
echo "Donwloading Smatch scoring script..."
wget $SMATCH_URL
tar zxvf smatch-v2.0.2.tar.gz

echo "Done!"