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

import parsing
import indexing



if __name__ == "__main__":
        if len(sys.argv)!=2:                # Expect exactly 1 argument
                sys.exit(2)

        path1 = sys.argv[1]
        
        parsing.parse_file(path1)

        indexing.create_index()

