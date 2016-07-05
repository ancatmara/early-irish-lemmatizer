## Old Irish Lemmatizer

A dictionary-based lemmatizer for Old, Middle and Early Modern Irish developed in the [School of Linguistics](https://ling.hse.ru/en/), NRU HSE.
The lemmatizer is able to predict lemmas for OOV-words and shows the average accuracy of 65,71 %. 

### Usage 

**Lemmatize a text**

*Lemmatizes the text from a file and writes the output into another file; returns a dictionary with non-dictionary forms and their counts*

```python
from lemmatizer import *
nondict = Lemmatizer.process_text(infile, outfile)
```

**Lemmatize all texts in the directory**

*Lemmatizes the text from all txt files in the directory and writes the output into the "lemmatized" folder; returns a dictionary with non-dictionary forms and their counts*

```python
nondict = Lemmatizer.process_files(path)
```

**Lemmatize a string*

*Initializes the Lemmatizer class for a string*

There are two available methods for now, 'baseline' and 'predict'. 'Baseline' returns lemmas for all dictionary words
and demutated forms for non-dictionary words; 'predict' predicts lemmas for non-dictionary words. The default method is 'predict'.

```python
lem = Lemmatizer(string, method='baseline')
lemmatizedString = lem.lemmaText
```

It has the following attributes:
* `lem.text` -- input string cleaned from punctuation and non-word symbols
* `lem.words` -- list of tokens
* `lem.lemmaText` -- lemmatized string 
* `lem.nondict` -- list of non-dictionary words
* `lem.recall` -- shows the percentage of dictionary forms in the string
* `lem.nr_tokens` -- number of tokens in a string
* `lem.nr_unique` -- number of unique tokens in a string

**Demutate standard input**

*Returns a demutated word*
```python
demutatedWord = Lemmatizer.demutate(word)
```

**Predict lemmas for non-dictionary forms**

*Takes a dictionary of OOV-words and their counts as input and creates two files for further manual revision:
OOV-words sorted by frequency higher than a given threshold (the  default one is 0) and a file with triplets of OOV-word, closest dictionary form and proposed lemma. 
Returns a corresponding list of tuples.*

```python
proposed = Lemmatizer.predict_lemmas(file_for_proposed, file_for_nondict, nondict, threshold=5)
```

**Update a dictionary**

*Adds words from a preformatted file ("lemma\tform1,form2...\n") to the "forms.json" dictionary*

```python
Lemmatizer.update_dict(path_to_dict, path_to_update)
```


### Evaluation

There is a gold standard of 50 random sentences from the test subcorpus available for evaluation (50\_gold\_test.txt) and a test script that computes accuracy of the lemmatizer's performance with default options (test\_lemmatizer.py). 
