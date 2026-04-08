ITALIAN DATA

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

EXTRACTION FROM COCA 


```
src/query_eng.py


```


```
(min 10 tokens max 100 tokens -clean text)
CLEANING DATA AND CREATION OF COLUMNS FOR DATASET

```

src/clean_data_eng.py

```
(one extraction for sentence)

SAMPLING FOR DATA CREATION

```
src/sample.py output in /dataset

```

SAMPLING 100 INSTANCING FOR INTER-ANNOTATOR AGREEMENT

```

python3 src/sample_agreement.py data/dataset/positive_ita_dataset.csv data/agreement/iat_pos_sampled.csv

python3 src/sample_agreement.py data/dataset/negative_ita_dataset.csv data/agreement/ita_neg_sampled.csv

python3 src/sample_agreement.py data/dataset/positive_eng_dataset.csv data/agreement/eng_pos_sampled.csv

python3 src/sample_agreement.py data/dataset/negative_eng_dataset.csv data/agreement/eng_neg_sampled.csv


```