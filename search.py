from Stemmer import Stemmer
import re
import sys
import os
import bisect
import timeit
import math


page_info = {}
index_files = sorted(os.listdir('index'))
index = {}


stemmer = Stemmer('english')
stemmer.maxCacheSize = 50000

stopwords= ['']
with open('stop_words.txt','r') as f:
    for line in f:
        stopwords.append(line.strip())


def get_tokens(text):
    tokens = re.findall(r'[a-zA-Z]+|[0-9]+',text)
    stemmed_tokens = stemmer.stemWords(tokens)
    token_list = []
    for token in stemmed_tokens:
        lower_case_token = token.lower()
        if (lower_case_token[:15]!='spamlinkreports' and lower_case_token not in stopwords):
            token_list.append(lower_case_token)
    return token_list


def get_page_info(file_path):
    global page_info
    with open(file_path,'r') as f:
        for line in f:
            x = line.split(',')
            page_info[x[0]] = (int(x[1]),x[2])


def tokenise_query(query):
    tokens = {'general':[],'t':[],'b':[],'i':[],'c':[],'l':[],'r':[]}
    field = None
    for word in query.lower().split():
        if word[1] == ':':
            if word[0] in ('t','b','i','c','l','r'):
                field = word[0]
        if field:
            tokens[word[0]]+=get_tokens(word)
        else:
            tokens['general']+=get_tokens(word)
    return tokens


def load_index(token):
    if not token in index:
        index_filename = index_files[bisect.bisect_left(index_files, token[:2])]
        with open(os.path.join('index',index_filename),'r') as f:
            lines = f.readlines()
        for i in range(len(lines)//2):
            term = lines[2*i].split(',')
            posting_list = lines[(2*i)+1].split(',')
            posting_list.pop(-1)
            index[term] = posting_list

def parse_termfreq(posting):
    docid, freq_string = posting.split('.')
    freq_list = re.findall(r'[tibrcl][0-9]+',freq_string)
    freq = {}
    for x in freq_list:
        freq[x[0]]=int(x[1:])
    return docid,freq

def rank(query_tokens):
    weight = {'t':2,'i':1,'b':0.3,'r':0.25,'c':0.75, 'l':0.15}
    doc_rank = {}
    for field in query_tokens.keys(): 
        for token in query_tokens[field]:
            if token in index.keys():
                for posting in index[token]:
                    docid, freq = parse_termfreq(posting)
                    tf = 0
                    for f in freq.keys():
                        tf+=freq[f]*weight[f]
                    tf /= page_info[docid][0]
                    idf = math.log10(25000000/(len(index[token])+1))
                    score = tf*idf
                    if field in freq.keys():
                        score*=3
                    if docid in doc_rank:
                        doc_rank[docid]+= score
                    else:
                        doc_rank[docid] = score
    return sorted(list(doc_rank.items()),key=lambda x:x[1],reverse=True)


if __name__ == '__main__':

    get_page_info('doc_info-chunk-101.txt')

    with open(sys.argv[1])as f:
        queries = f.readlines()

    for query in queries:

        start = timeit.default_timer()

        query_tokens = tokenise_query(query)
        for field in query_tokens.keys():
            for token in query_tokens[field]:
                load_index(token)
        print(list(page_info[x[0]][1] for x in rank(query_tokens)[:10]))    

        stop = timeit.default_timer()
        print ("time :- "+str(stop - start))

