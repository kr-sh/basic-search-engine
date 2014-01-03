###! /usr/bin/python

import sys
import math
import random
import re
from collections import OrderedDict,defaultdict
import pickle
from sets import Set
import time
import ranking
import os
import nltk

## unpickling the index
index = OrderedDict()
index = pickle.load(open("index","rb"))

def get_similar_words(query):
    similar_list = set()
    query_parts = query.strip().split()
    word = query_parts[1].strip()
    if re.search('\w+',word):                             ## if valid word entered for the request
##        text = nltk.Text(word.lower() for word in nltk.corpus.brown.words())
##        print text.similar(query_parts[1])

        path = ".//Extracted_text_files"
        dirlist = os.listdir(path)
        w1_list = list()
        w2_list = list()
        for input_file in dirlist:                                      ## for each of the cranfield text files
            with open(path + "//" + input_file,"r") as fi:                 ## open it in the read mode and parse
                lines = fi.read()
                if re.search('%s'% word,lines):
                    w1_list.append(re.findall('(\w+ %s \w+)'% word,lines))
##                    w2_list.append(re.findall('%s (\w+)'% word,lines))
##        print w1_list
##        print len(w1_list)

##        for w1 in w1_list:
##            if len(w1) != 0:
####                print w1[0],"\n"
##                w2 = w1[0].split(' ')
##                w2 = w2.strip().split(' ')
##                print w2
##        w1_set = set(w1_list)
                
##        print w2_list
        w2_set = set()
        for input_file in dirlist:                                      ## for each of the cranfield text files
            with open(path + "//" + input_file,"r") as fi:                 ## open it in the read mode and parse
                lines = fi.read()
                for w1 in w1_list:
                    if len(w1) != 0:
                        w2 = w1[0].split(' ')
##                        for word in index.keys():
##                            if (w2[0]+' ' + word + ' ' +w2[2]) in lines:
##                                w2_set.add(word)
##                                print word,"\n"
##        print w2_set
                        match = set(re.findall('{} (\w+) {}'.format(w2[0],w2[2]),lines))
                        if len(match) != 0:
                            similar_list = similar_list.union(match)
    print similar_list
##        
                
if __name__ == "__main__":
        if len(sys.argv)!=1:                # Expect exactly zero argument: the training data file
                sys.exit(2)
        query = raw_input('query: ')
        get_similar_words(query)
