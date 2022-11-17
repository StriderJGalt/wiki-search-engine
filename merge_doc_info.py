import os

if __name__ == '__main__':
    
    filenames = sorted(os.listdir('.'))
    doc_info_filenames = (x for x in filenames if x[:8]=='doc_info')

    doc_info = []

    for file in doc_info_filenames:
        with open(file,'r') as f:
            for line in f:
                doc_info.append(line.split(','))

    doc_info = sorted(doc_info,key=lambda x: x[0])
    with open('doc_info.txt','w') as f:
        for r in doc_info:
            f.write('{},{},{}'.format(r[0],r[1],r[2]))
