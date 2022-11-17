import sys
import re
import bz2
from Stemmer import Stemmer
# from multiprocessing import Pool

# def save_obj(obj, name ):
    # with open(name + '.pkl', 'wb') as f:
        # pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


stemmer = Stemmer('english')
stemmer.maxCacheSize = 50000

stopwords= ['']
with open('stop_words.txt','r') as f:
    for line in f:
        stopwords.append(line.strip())

MAX_INDEX_LENGTH = 1000000000
page_info = {}
index = {}
number_of_pages_in_index = 0
raw_tokens = set()
num_files_written = {}
index_folder_path = ''
filename = ''

def get_tokens(text):
    tokens = re.findall(r'[a-zA-Z]+|[0-9]+',text)
    raw_tokens.update(tokens)
    stemmed_tokens = stemmer.stemWords(tokens)
    token_list = []
    for token in stemmed_tokens:
        lower_case_token = token.lower()
        if (lower_case_token[:15]!='spamlinkreports' and lower_case_token not in stopwords):
            token_list.append(lower_case_token)
    return token_list


def process_page(pages):
    global number_of_pages_in_index
    fields = ('t','b','i','r','c','l')
    for page in pages:
        if any(x in page['t'] for x in ['Wikipedia:','Template:','File:','Ftp:']):
            continue
        page_tokens = set()
        for field in fields:
            tokens = get_tokens(page[field])
            page_tokens.update(tokens)
            for token in tokens:
                if not token in index:
                    index[token] = {}
                if not page['id'] in index[token]:
                    number_of_pages_in_index += 1
                    index[token][page['id']] = {}
                if not field in index[token][page['id']]:
                    index[token][page['id']][field] = 1
                else:
                    index[token][page['id']][field]+=1
        page_info[page['id']] = (len(page_tokens),page['t'])
    if number_of_pages_in_index > MAX_INDEX_LENGTH:
        dump_index()
        index.clear()
        number_of_pages_in_index = 0
        

# def make_index(pages):
#     p = Pool(processes=4)
#     indexes = p.map(process_page, pages, chunksize=50)
#     p.close()
#     p.join()
#     for i in indexes:
#         for token in i.keys():
#             if token not in index:
#                index[token] = {'t':[], 'b':[]}
#             index[token]['t'].append(i[token]['t'])
#             index[token]['b'].append(i[token]['b'])


class wikipedia_dump_handler():
    def __init__(self):
        self.pages = []
        self.id = None
        self.title = ''
        self.text = ''
        self.category = ''
        self.infobox = ''
        self.references = ''
        self.char_buffer = ''
        self.links = ''
        self.storing_text = False
        self.storing_references = False
        self.storing_infobox = False

    def parse(self,xml_file_path):
        # bzfile = bz2.open(xml_file_path,'rt')
        file = open(xml_file_path,'r')
        # with open(xml_file_path,'r') as f:
        # for line in bzfile:
        for line in file:
            if '<page>' in line:
                self.id = None
                self.title = ''
                self.text = ''
                self.category = ''
                self.infobox = ''
                self.references = ''
                self.char_buffer = ''
                self.storing_text = False
                self.storing_references = False
                self.storing_infobox = False
            elif '</page>' in line:
                self.pages.append({'id':self.id, 't':self.title, 'b':self.text, 'c': self.category,'r':self.references,'i':self.infobox, 'l':self.links})
                if len(self.pages) > 100:
                    process_page(self.pages)
                    # for p in self.pages:
                        # print('\n',p,'\n')
                    self.pages.clear()
            elif '<title>' in line:
                self.title = line.split('<title>')[1].split('</title>')[0]
            elif '<id>' in line:
                if not self.id:
                    self.id = int(line.split('<id>')[1].split('</id>')[0])
            elif '<text' in line:
                self.storing_text = True
                self.char_buffer = line.split('>')[1]
                if '{{Infobox' in line and not self.storing_infobox:
                    self.storing_infobox = True
                    self.storing_text = False
                    self.text += self.char_buffer 
                    self.char_buffer = line.split('{{Infobox')[1]
            elif '{{Infobox' in line and not self.storing_infobox:
                self.storing_infobox = True
                self.storing_text = False
                self.text += self.char_buffer 
                self.char_buffer = line.split('{{Infobox')[1]
            elif self.storing_infobox and line.strip() == '}}':
                self.storing_infobox = False
                self.storing_text = True
                self.infobox = self.char_buffer
                self.char_buffer = ''
            elif '==References==' in line:
                if self.storing_infobox:
                    self.storing_infobox = False
                    self.infobox = self.char_buffer
                if self.storing_text:
                    self.storing_text = False
                    self.text += self.char_buffer
                self.storing_references = True
                self.char_buffer = ''
                # urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', line)
                # for url in urls:
                #     self.links+=url+' '
            elif '[[Category:' in line:    
                if self.storing_references:
                    self.storing_references = False
                    self.references = self.char_buffer
                if self.storing_infobox:
                    self.storing_infobox = False
                    self.infobox = self.char_buffer
                self.category += line.split('[[Category:')[1]
                self.storing_text = True
                self.char_buffer = ''
            elif self.storing_infobox:
                self.char_buffer += line
                # urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', line)
                # for url in urls:
                #     self.links+=url+' '
            elif self.storing_text:
                self.char_buffer += line
                # urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', line)
                # for url in urls:
                #     self.links+=url+' '
            elif self.storing_references:
                self.char_buffer += line
                # urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', line)
                # for url in urls:
                #     self.links+=url+' '
            if '</text>' in line:
                if self.storing_text:
                    self.storing_text = False
                    if not '<text' in line:
                        self.char_buffer += line.split('</text>')[0]
                        self.text += self.char_buffer
                if self.storing_references:
                    self.char_buffer += line.split('</text>')[0]
                    self.references = self.char_buffer
                # urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', line)
                # for url in urls:
                #     self.links+=url+' '
        # bzfile.close()
        file.close()
        process_page(self.pages)


def dump_index():
    bigram_index = {}
    for token in index.keys():
        bigram = token[:2]
        if not bigram in bigram_index:
            bigram_index[bigram]=[token]
        else:
            bigram_index[bigram].append(token)

    for bigram in bigram_index:
        if bigram not in num_files_written:
            num_files_written[bigram]=0
        num_files_written[bigram]+=1    
        with open('{}{}-index-{}-{}.txt'.format(index_folder_path,bigram,filename,num_files_written[bigram]),'w') as f:
            for token in sorted(bigram_index[bigram]):
                token_dict = index[token]
                f.write('{},{}\n'.format(token,len(token_dict)))
                for page_id in sorted(token_dict.keys()):
                    f.write(str(page_id)+'.')
                    page = token_dict[page_id]
                    for field in page.keys():
                        f.write(field+str(page[field]))
                    f.write(',')
                f.write('\n')


if __name__ == '__main__':
    
    # check if correct number of arguments have been given
    if(len(sys.argv)!=3):
        print('Incorrect Number of arguments!')
        print('Usage: python3 indexer.py <path_to_wiki_dump> \
            <path_to_inverted_index_dir>')
    filepath = sys.argv[1]
    filename = filepath.split('/')[-1]
    index_folder_path = sys.argv[2]

    parser = wikipedia_dump_handler()
    parser.parse(filepath)

    with open('stat-'+filename.split('.')[0]+'.txt','w') as f:
        f.write(str(len(raw_tokens))+'\n')
        f.write(str(len(index.keys())))

    dump_index()

    with open('doc_info-'+filename.split('.')[0]+'.txt','w') as f:
        for docid in sorted(page_info.keys()):
            f.write(str(docid)+','+str(page_info[docid][0])+','+page_info[docid][1]+'\n')


    # save_obj(index, sys.argv[2]+'/ti')    
