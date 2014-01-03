###! /usr/bin/python

import sys
import math
import re
from collections import OrderedDict, defaultdict
from xml.dom.minidom import parse, parseString
import xml.dom.minidom as minidom
import os
import nltk
import pickle


metadata = defaultdict() 
def parse_file(path1):

    print "parsing files.."
    
    path2 = ".//Extracted_text_files"                   ## creating a directory in the current dir to store the extracted text files
    if not os.path.exists(path2):                       ## if directory does not exist, create it
        os.makedirs(path2)    
    dirlist = os.listdir(path1)                                     ## list all the cranfield text files in the input directory 
    
    for input_file in dirlist:                                      ## for each of the cranfield text files
        with open(path1 + "//" + input_file,"r") as fi:                 ## open it in the read mode and parse
                lines = fi.read()
                doc = minidom.parseString(lines)
                text = doc.getElementsByTagName('TEXT')
                docno_nodes = doc.getElementsByTagName('DOCNO')
                title_nodes = doc.getElementsByTagName('TITLE')
                for d in docno_nodes:
                    docid = d.firstChild.data.strip()
                with open(path2 + "//" + docid ,"w") as output_file:    ## write only the TEXT part to another file
                    for t1 in text:
                        file_text = t1.firstChild.data
                        output_file.write(file_text)
                output_file.close()
                for ti in title_nodes:                              
                    title = ti.firstChild.data.strip()                  ## extract the title and store in the metadata dictionary
                    metadata[docid] = title  
        fi.close()

    ## pickle the metadata dictionary for ranking
    pickle.dump(metadata,open("metadata","wb"))
    

if __name__ == "__main__":
        if len(sys.argv)!=1: # Expect exactly one argument: the training data file
                sys.exit(2)
                
        parse_file()
