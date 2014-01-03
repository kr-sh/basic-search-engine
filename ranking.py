###! /usr/bin/python

import sys
import math
import random
import re
from collections import OrderedDict,defaultdict
import pickle
from sets import Set
from operator import itemgetter
import os
import nltk
from nltk.tokenize.regexp import RegexpTokenizer
import time

index = pickle.load(open("index","rb"))
##score_dict = pickle.load(open("score_dict","rb"))
##pos_dict = pickle.load(open("pos_dict","rb"))
path = ".//Extracted_text_files"
dirlist = os.listdir(path) 

cnt = 0
## ranking is done based on scores- here, a descending order of scores is considered
def ranking(query,score_dict,pos_dict):
    global cnt
    cnt = 0
    
    for (docid, score) in sorted(score_dict.iteritems(), key = itemgetter(1),reverse =True):
        summarize(docid,score_dict,pos_dict)
    print "Total documents displayed for this query:", cnt

## summarization is done as extracting and displaying 8 words before and after the query occurrence
def summarize(docid,score_dict,pos_dict):
    global cnt
    tokenizer = RegexpTokenizer('\w+')    ##creating a tokenizer to match the words
    snippet = ""
    with open(path + "//" + docid,"r") as fi:  ## open the extracted text file in read mode
        file_text = fi.read()
        tokens = tokenizer.tokenize(file_text)  ## tokenize the text file using the tokenizer

        if score_dict[docid] not in (0,-1):                 ## for normal phrase/word queries
            cnt += 1 
            for pos in pos_dict[docid]:                     ## get snippets based on identified positions from the position dictionary
                pos1 = abs(pos - 8)                         ## get the preceeding and following 8 words from the identified position in the text
                pos2 = pos + 8
                if pos1 < 0:
                    pos1 = 0
                if pos2 > len(tokens):
                    pos2 = len(tokens)
                snippet = ' '.join(tokens[pos1:pos2])       
                print docid,"\t",snippet                    ## display docid and snippet
        elif score_dict[docid] == -1:                       ## to display document ids that do not contain the negated word/phrase
            cnt += 1
            print docid

                
    

if __name__ == "__main__":
        if len(sys.argv)!=1: # Expect exactly one argument: the training data file
                sys.exit(2)

##        start = time.clock()
        ranking()
##        elapsed = (time.clock() - start)
##        print elapsed

