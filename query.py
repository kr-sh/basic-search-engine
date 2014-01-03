###! /usr/bin/python

import sys
import math
import random
import re
from xml.dom.minidom import parse, parseString
import xml.dom.minidom as minidom
from collections import OrderedDict,defaultdict
import pickle
from sets import Set
from operator import itemgetter
import os
import nltk
from nltk.tokenize.regexp import RegexpTokenizer
import time
import Queue

import querying


if __name__ == "__main__":
        if len(sys.argv)!=1:                # Expect exactly zero argument: the training data file
                sys.exit(2)
        
        ## lists storing the negated and normal query words and phrases
        words_list = list()
        phrase_list = list()
        negphrase_list = list()
        negwords_list = list()

        querying.get_query()

