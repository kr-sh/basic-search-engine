###! /usr/bin/python

import sys
import math
import random
import re
from collections import OrderedDict
from xml.dom.minidom import parse, parseString
import xml.dom.minidom as minidom
import os
import pickle
import time
import nltk
##from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

## This function creates the index for the Cranfield corpus.
## The index stores the [word][docid] pairs as keys and the positions of that word in the docid as values 

def create_index():

    ## stopwords from nltk.corpus
    stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']
    
    print "creating index.."
    start = time.clock()
    path1 = ".//Extracted_text_files"
    dirlist = os.listdir(path1)                             ## list all the extracted text files
    index =  OrderedDict()
    porter = nltk.PorterStemmer()
    for input_file in dirlist:                              ## for each text file
        count = 0
        docid = input_file.strip()          
        with open(path1 + "//" + input_file,"r") as input_line:                     ## open the text file in read mode
                lines = input_line.read().strip()
                words = re.findall(r'\w+', lines,flags = re.UNICODE | re.LOCALE)    ## extract words from the text
                for word in words:                          ## for each word
                    count +=1                               ## count is calculated to get the word position, hence count indicates the word's position
                    word = word.lower().strip()             ## lower-case the word
                    word = porter.stem(word)                ## stemming the words before inserting into the index
                    if index.__contains__(word):            ## check if index contains the word
                        if index[word].__contains__(docid):     ## check if there is a doc containing this word
                            index[word][docid].append(count)        ## if yes, append the new position to previous positions
                        else:                                   ## else create an entry for this new doc containing this word
                             index[word][docid] = []                ## initialize the value for this docid and 
                             index[word][docid].append(count)       ## insert the position into the index entry against this docid
                    else:                                   ## if word not in index, create an index entry for this word
                             index[word]= OrderedDict()
                             index[word][docid] = []
                             index[word][docid].append(count)   ## insert the position against the current docid                  

    for word in stopwords:                 ## removing stop-words from the index
        word = porter.stem(word)
        if word in index.keys():
            del index[word]
     
    ## pickle the index dictionary for querying and ranking                    
    pickle.dump(index,open("index","wb"))
    elapsed = (time.clock() - start)
    print elapsed

if __name__ == "__main__":
        if len(sys.argv)!=1: # Expect exactly one argument: the training data file
                sys.exit(2)
                
        create_index()

