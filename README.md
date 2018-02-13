CAMR: A transition-based AMR Parser
==========

CAMR is a transition-based, tree-to-graph parser for the [Abstract Meaning Representation](http://amr.isi.edu/) of a sentence. It is a product of an on-going collaboration between the [Chinese Language Processing Group](http://www.cs.brandeis.edu/~clp/Lab/Home.html) at Brandeis University and [`cemantix.org`](http://cemantix.org)

Reference:

- Chuan Wang, Nianwen Xue, and Sameer Pradhan.2015. [A transition-based algorithm for AMR parsing](http://aclweb.org/anthology/N/N15/N15-1040.pdf). In Proceedings of the 2015 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, pages 366–375, Denver, Colorado, May–June. Association for Computational Linguistics.

```
@InProceedings{wang-xue-pradhan:2015:NAACL-HLT,
  author    = {Wang, Chuan  and  Xue, Nianwen  and  Pradhan, Sameer},
  title     = {A Transition-based Algorithm for AMR Parsing},
  booktitle = {Proceedings of the 2015 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies},
  month     = {May--June},
  year      = {2015},
  address   = {Denver, Colorado},
  publisher = {Association for Computational Linguistics},
  pages     = {366--375},
  url       = {http://www.aclweb.org/anthology/N15-1040}
}
```

- Chuan Wang, Nianwen Xue, and Sameer Pradhan.2015. [Boosting Transition-based AMR Parsing with Refined Actions and
Auxiliary Analyzers](https://aclweb.org/anthology/P/P15/P15-2141.pdf). In Proceedings of the 53rd Annual Meeting of the Association for Computational Linguistics and the 7th International Joint Conference on Natural Language Processing (Short Papers), pages 857-862, Beijing, China, July 26-31, 2015. Association for Computational Linguistics.

```
@InProceedings{wang-xue-pradhan:2015:ACL-IJCNLP,
  author    = {Wang, Chuan  and  Xue, Nianwen  and  Pradhan, Sameer},
  title     = {Boosting Transition-based AMR Parsing with Refined Actions and Auxiliary Analyzers},
  booktitle = {Proceedings of the 53rd Annual Meeting of the Association for Computational Linguistics and the 7th International Joint Conference on Natural Language Processing (Volume 2: Short Papers)},
  month     = {July},
  year      = {2015},
  address   = {Beijing, China},
  publisher = {Association for Computational Linguistics},
  pages     = {857--862},
  url       = {http://www.aclweb.org/anthology/P15-2141}
}
```

- Chuan Wang, Nianwen Xue, Sameer Pradhan, Xiaoman Pan, and Heng Ji. 2016. [CAMR at SemEval-2016 task 8: An extended transition-based AMR parser](http://m-mitchell.com/NAACL-2016/SemEval/pdf/SemEval163.pdf). In Proceedings of the 10th International Workshop on Semantic Evaluation (SemEval 2016), San Diego, California, June. Association for Computational Linguistics.

```
@InProceedings{wang-EtAl:2016:SemEval,
  author    = {Wang, Chuan  and  Pradhan, Sameer  and  Pan, Xiaoman  and  Ji, Heng  and  Xue, Nianwen},
  title     = {CAMR at SemEval-2016 Task 8: An Extended Transition-based AMR Parser},
  booktitle = {Proceedings of the 10th International Workshop on Semantic Evaluation (SemEval-2016)},
  month     = {June},
  year      = {2016},
  address   = {San Diego, California},
  publisher = {Association for Computational Linguistics},
  pages     = {1173--1178},
  url       = {http://www.aclweb.org/anthology/S16-1181}
}
```
# Updates

## Custom updates (YP)

* Before running anything, source the script which 
sets environment variables:
    
    ```bash
    
    source ./scripts/set_env.sh
    
    ```
    This sets the variables which are used throughout the code.
    
* Changed the `./config.sh` script to include the correct 
version of the CoreNLP tool.

* Changed the `./stanfordnlp/default.properties` file 
by adding the 'ssplit.eolonly=true' option. 
Previously, CoreNLP would split sentences, 
even if they constitute a text for one AMR. 
This resulted in a mismatch between the number of AMRs 
and processed textual descriptions.

* To install bllipparser on Anaconda environments, run:

```bash

conda install -c steven_c bllipparser

```

## Official updates

09-2016 We have included the retrain instruction.

08-2016 We have  new model trained on bigger dataset.
released
# Dependencies

First download the project:
      
      git clone https://github.com/Juicechuan/AMRParsing.git

Here we use a modified version of the [Stanford CoreNLP python wrapper](https://github.com/dasmith/stanford-corenlp-python), [Charniak Parser](https://github.com/BLLIP/bllip-parser) and [Stanford CoreNLP toolkit](http://nlp.stanford.edu/software/corenlp.shtml).
To setup dependencies, run the following script:
   
      ./scripts/config.sh

>**Note:** For Mac users, there are some problems when installing the Charniak Parser python module bllipparser. We recommend to use Linux system in order to utilize the Charniak Parser. Also you may need [swig](http://www.swig.org/) to successfully install bllipparser.

# Parsing with Pre-trained Model
The input data format for parsing should be raw document with one sentence per line. 
##Preprocessing
To preprocess the data, run:
   
      python amr_parsing.py -m preprocess [input_sentence_file]

This will give you the tokenized sentences(.tok), POS tag and name entity (.prp) and dependency structure (.charniak.parse.dep) (generated by Charniak parser and Stanford Dependency converter).
>**Note:** The parser will try to read the preprocessed file with the above suffix. So if the preprocessing is not complete, do remove all the cached file and then re-run this step.

## Parsing
Download the following model: 

[LDC2014T12](http://www.cs.brandeis.edu/~cwang24/files/amr-anno-1.0.train.m.tar.gz): trained on training set of LDC2014T12.

[SemEval2016](http://www.cs.brandeis.edu/~cwang24/files/amr-semeval-all.train.m.tar.gz): trained on training set of SemEval 2016 Task 8.

Uncompress the model file, then use the following command to parse the sentence:

      python amr_parsing.py -m parse --model [model_file] [input_sentence_file] 2>log/error.log

This will give your the parsed AMR file(.parsed) in the same directory of your input sentence file. 

> **Note:** 
> these models doesn't incorporate the Semantic Role Label feature, so it will give you slightly lower results reported in the papers. We are working on integrating the SRL system into the pipeline.  

# Retrain the parser
If you would like to retrain the parser, you first have to obtain the alignment in the following section.

## Alignment
If you have annotated AMR file, you could first run the preprocessing step:
	
	python amr_parsing.py -m preprocess --amrfmt amr [input_amr_file]

This will generate a tokenized AMR file (.amr.tok) (which has :tok tag in the comments). Then you can run the following command to get the aligned AMR file(.aligned)

	./scripts/jamr_align.sh [input_amr_tok_file]


> **Note:** We use [JAMR](https://github.com/jflanigan/jamr) to get the alignment between sentence and its AMR annotation. You need to download and set up JAMR.

## Retrain

To retrain the model with the provided feature template *basic_abt_brown_feats.templates* , use the following command:

      python2.7 amr_parsing.py -m train --amrfmt amr --verblist --smatcheval --model [path_to_save_model] -iter [iter_number] --feat ./feature/basic_abt_brown_feats.templates [path_to_train_amr_file] -d [path_to_dev_amr_file] > [log_file] 2>&1 &

The parser will be trained using basic feature template mentioned in our NAACL 2015 paper. 

> **Note:**
> - Since in the preprocessing step we don't include the Semantic Role Labeling feature, it wouldn't replicate the optimal results. 
> - If you want to retrain the model with different features, you will have to get your hands dirty with the feature template file with examples defined in temp/ folder and modify the feature functions in model.py/newstate.py. 
