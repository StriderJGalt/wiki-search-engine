#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import bz2
import sys

# In[6]:


def split_xml(filename,pages_per_chunk,num_chunks_to_process=False):
    ''' The function gets the filename of wiktionary.xml.bz2 file as  input and creates
    smallers chunks of it in a the diretory chunks
    '''
    # Read line by line
    try:
        bzfile = bz2.BZ2File(filename)
    except:
        print('Couldnt open source file')
        return
    
    # Check and create chunk diretory
    # if not os.path.exists("chunks"):
        # os.mkdir("chunks")

    # Counters
    pagecount = 0
    filecount = 1
    #open chunkfile in write mode
    chunkname = lambda filecount: os.path.join("chunksof1lpages",filename.split('/')[2][:-8]+'-'+str(filecount)+".xml.bz2")
    chunkfile = bz2.BZ2File(chunkname(filecount), 'w')
    
    for line in bzfile:
        chunkfile.write(line)
        # the </page> determines new wiki page
        if b'</page>' in line:
            pagecount += 1
        if pagecount > pages_per_chunk:
            #print chunkname() # For Debugging
            chunkfile.close()
            if num_chunks_to_process and filecount >= num_chunks_to_process:
                return
            pagecount = 0 # RESET pagecount
            filecount += 1 # increment filename           
            chunkfile = bz2.BZ2File(chunkname(filecount), 'w')
    try:
        chunkfile.close()
    except:
        print("Files already close")


# In[11]:

if __name__ == '__main__':
    # print(sys.argv[1])
    split_xml(sys.argv[1],100000)
    # split_xml('enwiki-20210720-pages-articles-multistream.xml.bz2',500000)


# In[ ]:




