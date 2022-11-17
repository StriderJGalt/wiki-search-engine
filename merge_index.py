import os
import sys
import itertools
import bisect
from collections import defaultdict

if __name__ == '__main__':
    index_files_char = sys.argv[1]
    
    filenames = sorted(os.listdir('index'))
    selected_filenames = filenames[bisect.bisect_left(filenames, index_files_char):bisect.bisect_left(filenames, chr(ord(index_files_char) + 1))]
    
    file_groups = []
    iterator = itertools.groupby(selected_filenames, lambda x:x[:2])
    for element, group in iterator:
        file_groups.append(list(group))

    for group in file_groups:
        index = defaultdict(list)
        for file in group:
            with open(os.path.join('index',file),'r') as f:
                lines = f.readlines()
            for i in range(len(lines)//2):
                term,num_docs = lines[2*i].split(',')
                posting_list = lines[(2*i)+1].split(',')
                posting_list.pop(-1)
                index[term]+=posting_list
        with open(os.path.join('merged_index',group[0][:8]+'.txt'),'w') as f:
            for key in index.keys():
                f.write(key+'\n')
                for posting in index[key]:
                    f.write(posting+',')
                f.write('\n')
