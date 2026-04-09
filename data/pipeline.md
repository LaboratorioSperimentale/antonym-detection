# ITALIAN DATA


GENERATION OF QUERY
```
src/build_regex.py
```


EXTRACTION FROM CORIS
```
src/get_data.py
```


CLEANING DATA AND CREATION OF COLUMNS FOR DATASET
```
src/clean_data.py
```
(one extraction for sentence - min 10 tokens max 100 tokens -clean text)





# ENGLISH DATA


EXTRACTION FROM COCA (from COCA on server)
```
python3 extract_patterns.py /media/CORPORA/CORPORA/COCA
```
(min 10 tokens max 100 tokens - clean text)


CLEANING DATA AND CREATION OF COLUMNS FOR DATASET
```
python3 src/clean_data_eng.py \
  --input data/output_eng.tsv \
  --output data/output_clean_eng.tsv \
  --yes data/yes_instances_eng.tsv \
  --no data/no_instances_eng.tsv
```

(one extraction for sentence)





# DATASET CREATION


SAMPLING FOR DATASET CREATION
```
python3 src/sample.py \
  --input data/output_clean_eng.tsv \
  --output_yes data/dataset/eng_positive.tsv \
  --output_no data/dataset/eng_negative.tsv

python3 src/sample.py \
  --input data/output_clean.tsv \
  --output_yes data/dataset/ita_positive.tsv \
  --output_no data/dataset/ita_negative.tsv
```
(yes pattern-seed max 100 items / no pattern-seed max 150 items)

SAMPLING 100 INSTANCING FOR INTER-ANNOTATOR AGREEMENT
```
python3 src/sample_agreement.py data/dataset/ita_positive.tsv data/agreement/ita_pos_sampled.tsv

python3 src/sample_agreement.py data/dataset/ita_negative.tsv data/agreement/ita_neg_sampled.tsv

python3 src/sample_agreement.py data/dataset/eng_positive.tsv data/agreement/eng_pos_sampled.tsv

python3 src/sample_agreement.py data/dataset/eng_negative.tsv data/agreement/eng_neg_sampled.tsv
```