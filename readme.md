## Installation of libraries
pip install PyStemmer

## To run

for splitting bz2 dump,
first modify the number of pages per chunk in the code if needed and then run

`$python3 dsplit.py <path_to_bz2_file>`

for indexing

```$ python3 indexer.py <path_to_wiki_dump.bz2> <path_to_inverted_index_dir> ```

for merging index

```
$ for i in [a..z];
do 
	python3 merge_index.py $i
done
```

for merging page_info

```$python3 merge_page_info.py```

for searching

```$ python3 search.py <path_to_input_queries_file>```

