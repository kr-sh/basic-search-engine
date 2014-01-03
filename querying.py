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
from nltk.stem.porter import PorterStemmer


## unpickling the index
index = OrderedDict()
index = pickle.load(open("index","rb"))
porter = nltk.PorterStemmer()

## processing phrases in the query that are not negated -- put their information in the 2 result dictionaries- score_dict,pos_dict
def process_phrase(phrase_list,score_dict,pos_dict):
    
    for phrase in phrase_list:                  ## for each of the phrases entered in the query
        common_docid_set = set()                ## this set stores the docids that contain all the phrase words in the same doc

        phrase_words = phrase.strip().split()   ## split phrase into phrase-words
        
        for i in range(0,len(phrase_words)):    ## stemming the phrase words as index is stemmed
            phrase_words[i] = porter.stem(phrase_words[i])
            
        if len(phrase_words) == 1:              ## if only one word in the phrase 
            words_list.append(phrase_words[0])                          ## add it to the word list to process as a normal word in the query
        else:                                   ## else
            if phrase_words[0] in index.keys():                     ## if the first phrase-word is in index
                common_docid_set = set(index[phrase_words[0]].keys())   ## add it's docids to the set containing the common docids

            for i in range(1,len(phrase_words)):
                if phrase_words[i] in index.keys():                     ## if the next phrase-word is in the index
                    common_docid_set = set(index[phrase_words[i]].keys()) & common_docid_set    ## find the docids that are common with the previous words in the phrase
                else:                                                   ## if one of the phrase words is not in index, it implies the phrase does not occur in any document
                    common_docid_set.clear()                            ## hence empty the common doc set and break
                    break

            for docid in common_docid_set:                          ## for each doc containing the phrase-words, find if they occur together as a phrase
                prev_pos_set = set(index[phrase_words[0]][docid])       ## stores the positions of the first phrase-word
                curr_pos_set = set()
                for j in range(1,len(phrase_words)):    
                    for pos in index[phrase_words[i]][docid]:           ## for each position of the current phrase-word in current doc
                        curr_pos_set.add(pos-j)                             ## decrement the positions by j to match the start position of the phrase
                    correct_pos_set = curr_pos_set & prev_pos_set       ## stores the start positions of only those instances where the words appear next to each other 
                    if len(correct_pos_set) == 0:                       ## if there are no such positions in this doc where the words appear as a phrase
                        break                                               ## break and move to the next doc
                    else:
                        prev_pos_set = correct_pos_set                      ## else make current position set as the previous and move to the next word in the phrase

                if len(correct_pos_set) == 0:                       ## if pos set is empty, it implies there is no phrase match in current document
                    continue                                            ## hence continue to next document
                else:                                               ## else make the entry in the 2 result dictionaries for this phrase
                    if docid not in score_dict:                         ## if new docid entry in dict
                        score = len(correct_pos_set)*len(phrase_words)      ## score = no of occurrences * no of phrase words
                        score_dict[docid] = score                           ## storing docids with no of occurrences
                        pos_dict[docid] = correct_pos_set                   ## storing docids and start positions of phrase occurrences
                    else:                                            ## if existing docid, add occurrences and new phrase positions
                        score = score_dict[docid] + (len(correct_pos_set)*len(phrase_words))      ## add the scores for this phrase with the previous scores for this doc
                        score_dict[docid] = score
                        pos_dict[docid] = pos_dict[docid].union(correct_pos_set)  ## append the start positions for this phrase in the same doc       


## processing individual words in the query that are not negated -- put their info in the 2 result dictionaries
def process_words(words_list,score_dict,pos_dict):
    
    for q_word in words_list:                               ## for each word in the query
        q_word = q_word.strip()
        if q_word in index:                                 ## check if query word is in index
            for docid in index[q_word].keys():
                score = 0
                if docid not in score_dict:                                     ## if the docid is a new entry
                    score_dict[docid] = len(index[q_word][docid])                       ## store score = no of occurrences of that word                                 ## storing the score = no of occurrences of the word in the current doc
                    pos_dict[docid] = set(index[q_word][docid])                         ## store positions of word occurrences in the current doc
                else:                                                           ## if docid already exists in dict
                    score = score_dict[docid] + len(index[q_word][docid])               ## store score = previous score of the doc + no of occurrences of current word in same doc
                    score_dict[docid] = score
                    pos_dict[docid] = pos_dict[docid].union(set(index[q_word][docid]))  ## append the positions of this word in the current doc to existing position set 
  
## This function does the pre-processing. i.e matches the phrase and word patterns to extract the phrases/negated-phrases and words/negated-words from the query
def pre_process_query(query):
    global words_list
    global phrase_list
    global negphrase_list
    global negwords_list
    global index
    words_list = list()
    phrase_list = list()
    negphrase_list = list()
    negwords_list = list()
    
    negphrase_pat = re.compile('!\"(.*?)\"')
    negphrase_list = negphrase_pat.findall(query)
##    for negphrase in negphrase_m:
##        negphrase_list.append(porter.stem(negphrase))
    query = re.sub('!\"(.*?)\"','',query).strip()
    
    phrase_pat = re.compile('\"(.*?)\"')
    phrase_list = phrase_pat.findall(query)
##    for phrase in phrase_m:
##        phrase_list.append(porter.stem(phrase_m))
    query = re.sub('\"(.*?)\"','',query).strip()

    negword_pat = re.compile(r'!(\w+)+')
    negwords_m = negword_pat.findall(query)
    for negword in negwords_m:
        negwords_list.append(porter.stem(negword))
    query = re.sub(r'!(\w+)+','',query).strip()    
    
    word_pat = re.compile(r'\w+')
    words_m = word_pat.findall(query)
    for word in words_m:
        words_list.append(porter.stem(word))
    query = re.sub(r'\w+','',query).strip()

## This function calculates the statistics like df, tf and freq of words/phrases
def get_statistics(query,score_dict,pos_dict):
    
    query_parts = query.strip().split()
    pre_process_query(' '.join(query_parts[1:]))
    
    if query_parts[0] == 'df':                                      ## if query is to calculate df
        df = 0
        if re.search('\"(.*?)\"',query):                                ## check if query is for a phrase
            process_phrase(phrase_list,score_dict,pos_dict)                 ## process the phrase
            process_words(words_list,score_dict,pos_dict)                   ## for cases where users enter a phrase of one word
            for docid in score_dict.keys():
                if score_dict[docid] > 0:                               ## Phrase occurrences will have scores >0
                    df += 1                                             ## count all such docids from the score dict
            print df                                                        
        else:                                                           ## else query is for a word
            word = porter.stem(query_parts[1])
            if word in index.keys():                                    ## check if word is in index
                print len(index[word].keys())                               ## using the index get the no of docs in which the word appears
            else:                                                       ## else print 0
                print "0"

    if query_parts[0] == 'tf':                                      ## if query is to calculate tf
        if re.search('\[0-9]+',query_parts[1]) or len(query_parts) != 3:       ## error handling
            print "Please enter a valid query: tf docid term"
        else:
            docid = query_parts[1]                                  ## extract docid
            word = query_parts[2]                                   ## extract word
            word = porter.stem(word)                                ## stemming the word as indexed words are stemmed
            if word in index.keys():
                if docid in index[word].keys():                         ## check if docid in index
                    print len(index[word][docid])                            ## using the index get the no of occurrences of the word in the doc 
                else:                                                   ## else print 0
                    print "Word not present in this document ID as per index."
            else:
                print "Word not indexed."

    if query_parts[0] == 'freq':                                    ## if query is to calculate freq of a phrase
        process_phrase(phrase_list,score_dict,pos_dict)                 ## process the phrase
        process_words(words_list,score_dict,pos_dict)                   ## for cases where users enter a phrase of one word, process the word                   
        freq = 0
        for docid in pos_dict.keys():
            freq = freq + len(pos_dict[docid])    ## using the doc dict get the freq by adding the no of occurrences of the phrase for each doc in which the phrase appears
        print freq           

## get metadata - in this case only the title and text(data)
def get_metadata(query,score_dict,pos_dict):

    query_parts = query.strip().split()
    metadata = pickle.load(open("metadata","rb"))                   ## unpickle the metadata dictionary
    docid = query_parts[1]                                          ## retrieve the docid from the query
    path = ".//Extracted_text_files"
    if query_parts[0] == 'title':                                   ## get the title for a given docid
        print metadata[docid]
    if query_parts[0] == 'doc':                                     ## get the text for a given docid
        with open(path + "//" + docid,"r") as fi:
            lines = fi.read()
            print lines
        fi.close()
        
## This function finds the similar words from the nltk corpus
def get_similar_words(query):
    similar_set = set()
    query_parts = query.strip().split()
    word = query_parts[1].strip()
    if re.search('\w+',word):                             ## if valid word entered for the request
        path = ".//Extracted_text_files"
        dirlist = os.listdir(path)
        w1_list = list()
        w2_list = list()
        for input_file in dirlist:                                      ## for each of the cranfield text files
            with open(path + "//" + input_file,"r") as fi:                 ## open it in the read mode and parse
                lines = fi.read()
                if re.search('%s'% word,lines):
                    w1_list.append(re.findall('(\w+ %s \w+)'% word,lines))

        w2_set = set()
        for input_file in dirlist:                                      ## for each of the cranfield text files
            with open(path + "//" + input_file,"r") as fi:                 ## open it in the read mode and parse
                lines = fi.read()
                for w1 in w1_list:
                    if len(w1) != 0:
                        w2 = w1[0].split(' ')
                        match = set(re.findall('{} (\w+) {}'.format(w2[0],w2[2]),lines))
                        if len(match) != 0:
                            similar_set = similar_set.union(match)
        if  len(similar_set) != 0:
            print similar_set
        else:
            print "No such word in the corpus."
    
    else:                                                               ## error handling
        print "Please enter a valid query: similar term"
        
## retrieve the documents for the query and store results in the 2 result dictionaries
def get_documents(query,score_dict,pos_dict):
    global words_list
    global phrase_list
    global negphrase_list
    global negwords_list
    global index

    common_docid_set = set()

    pre_process_query(query)

    all_negative_phrase_docs = defaultdict() ## stores the docids of all the phrases that are negated i.e it stores docids which contain the negated phrase
    all_negative_word_docs = defaultdict()   ## stores the docids of all words that are negated i.e it stores docids which contain the negated word
    
    ## processing phrases in the query that are not negated -- put their information in the 2 result dictionaries
    process_phrase(phrase_list,score_dict,pos_dict)

    ## processing phrases in the query that are negated -- put their info in a separate dict 'all_negative_phrase_docs'
    ## functionality is the same as the processing for a normal phrase, but stored in a separate dict
    for phrase in negphrase_list:
        
        phrase_words = phrase.strip().split()               ## split phrase into phrase-words
        for i in range(0,len(phrase_words)):                ## stemming the phrase words as index is stemmed
            phrase_words[i] = porter.stem(phrase_words[i])
        
        if len(phrase_words) == 1:                          ## if only one word in the phrase 
            words_list.append(phrase_words[0])                          ## add it to the word list to process as a normal word in the query
        else:                                               ## else
            if phrase_words[0] in index.keys():                         ## if the first phrase-word is in index
                common_docid_set = set(index[phrase_words[0]].keys())   ## add it's docids to the set containing the common docids

            for i in range(1,len(phrase_words)):
                if phrase_words[i] in index.keys():                     ## if the next phrase-word is in the index
                    common_docid_set = set(index[phrase_words[i]].keys()) & common_docid_set    ## find the docids that are common with the previous words in the phrase
                else:                                                   ## if one of the phrase words is not in index, it implies the phrase does not occur in any document
                    common_docid_set.clear()                            ## hence empty the common doc set and break
                    break

            for docid in common_docid_set:                          ## for each doc containing the phrase-words, find if they occur together as a phrase
                prev_pos_set = set(index[phrase_words[0]][docid])       ## stores the positions of the first phrase-word
                curr_pos_set = set()
                for j in range(1,len(phrase_words)):    
                    for pos in index[phrase_words[i]][docid]:           ## for each position of the current phrase-word in current doc
                        curr_pos_set.add(pos-j)                             ## decrement the positions by j to match the start position of the phrase
                    correct_pos_set = curr_pos_set & prev_pos_set       ## stores only the start positions of those instances where the words appear next to each other 
                    if len(correct_pos_set) == 0:                       ## if there are no such positions in thid doc where the words appear as a phrase
                        break                                               ## break and move to the next doc
                    else:
                        prev_pos_set = correct_pos_set
                        
                if len(correct_pos_set) == 0:               ## if pos set is empty, it implies that no phrase match in current document
                    continue                                    ## hence continue to next document
                else:                                       ## else make the entry in the doc dict for positive phrase
                    if docid not in all_negative_phrase_docs:           ## if new docid entry in dict
                        score = len(correct_pos_set)*len(phrase_words)      ## score = no of occurrences * no of phrase words
                        all_negative_phrase_docs[docid] = score             ## storing docids with no of occurrences
                    else:                                               ## if existing docid, add occurrences and new positions
                        score = all_negative_phrase_docs[docid] + (len(correct_pos_set)*len(phrase_words))      ## add the scores for the next phrase in the same doc
                        all_negative_phrase_docs[docid] = score         ## storing the scores just to maintain consistency, scores will not be used for document retrieval

    
    ## processing individual words in the query that are not negated -- put their info in the 2 result dictionaries
    process_words(words_list,score_dict,pos_dict)

    ## processing individual words in the query that are negated -- put their info in a separate dict 'all_negative_word_docs'
    ## functionality is the same as processing a normal word, but stored in a separate dict
    for q_negword in negwords_list:
        q_negword = q_negword.strip()
        if q_negword in index:
            for docid in index[q_negword].keys():
                score = 0
                if docid not in all_negative_word_docs:
                    all_negative_word_docs[docid] = len(index[q_negword][docid])            ## stores the docids in a separate dict for negated words     
                else:
                    score = all_negative_word_docs[docid] + len(index[q_negword][docid])    ## storing the scores just to maintain consistency in code, scores are not used in document retrieval
                    all_negative_word_docs[docid] = score                                                                   

    ## get the set of documents that contains negated phrases or negated words
    negative_phrase_set = set()
    negative_word_set = set()
    if len(all_negative_phrase_docs.keys()) != 0:                                           ## if there is a negated phrase in the query, the all_negative_phrase_docs will contain docids containing the phrase
        negative_phrase_set = set(score_dict.keys()) - set(all_negative_phrase_docs.keys())     ## thus taking the difference from the whole set of documents will give the set not containing that phrase
    if len(all_negative_word_docs.keys()) != 0:                                             ## if there is a negated word in the query, the all_negative_word_docs will contain docids containing the word
        negative_word_set = set(score_dict.keys()) - set(all_negative_word_docs.keys())         ## thus taking the difference from the whole set of documents will give the set not containing that word

    total_negative_set = negative_phrase_set | negative_word_set                            ## union of these 2 sets gives the set of documents not containing the phrase/words that are negated in the query

    ## to get the final set of documents, we need to do a fuzzy or between the normal(score_dict) and negated set (total_negative_set) of documents
    ## As per the following logic, if there is a docid common to both the normal set and the negated set, it will retain it and show phrase/word instances from the normal set.
    ## else the negated docid set is identified by assigning them a negative score
    for docid in total_negative_set:                                                        ## for each docid in the negated set of documents
        if score_dict[docid] == 0:                                                       
            score_dict[docid] = -1

    ## pickle the final dictionaries for ranking
##    pickle.dump(score_dict,open("score_dict","wb"))
##    pickle.dump(pos_dict,open("pos_dict","wb"))

    ## call the ranking function to rand and display snippets
    ranking.ranking(query,score_dict,pos_dict)


## takes the query as input and calls the appropriate function to get statistics, metadata or retrieve documents
def get_query():

    ## 2 result dictionaries
    score_dict = defaultdict() 
    pos_dict = defaultdict()    
    
    while True:
            
        query = raw_input("enter query: ")
        print "retrieving results.."
        start = time.clock()
        
        for i in range(1,1401):                     ## initializing the score dictionary with 0 scores for all docids
            score_dict[str(i)] = 0
        for i in range(1,1401):                     ## initializing the position dictionary with an empty position set for all docids
            pos_dict[str(i)] = set()        

        query_parts = query.strip().split()         ## split the query to understand the request type
        if query_parts[0] in ('df', 'tf', 'freq'):      ## if query is to calculate the tf,df or freq, then call get_statistics
            get_statistics(query,score_dict,pos_dict)
        elif query_parts[0] in ('title','doc'):         ## if query is to get the text or title, call get_metadata
            get_metadata(query,score_dict,pos_dict)
        elif query_parts[0] in ('similar'):
            get_similar_words(query)
        else:                                           ## else call get_documents
            get_documents(query,score_dict,pos_dict)

## claculate the time elapsed for returning results
        elapsed = (time.clock() - start)
        print elapsed


if __name__ == "__main__":
        if len(sys.argv)!=1:                # Expect exactly zero argument: the training data file
                sys.exit(2)

        
        get_query()

