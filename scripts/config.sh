#!/bin/bash

# Models of the Stanford tools used
CORENLP_DIR="stanford-corenlp-full-2015-04-20"
STANFORD_PARSER_DIR="stanford-parser-full-2014-01-04"

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

echo "Setup Charniak Parser ..."
pip install --user bllipparser
