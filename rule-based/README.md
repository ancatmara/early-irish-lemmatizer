## Old Irish Lemmatizer

A lexicon-based lemmatizer for Old, Middle and Early Modern Irish developed in the [School of Linguistics](https://ling.hse.ru/en/), NRU HSE.
The lemmatizer is able to predict lemmas for OOV-words and shows the average accuracy of 65,71 %. 

### Usage 

**Lemmatize a text**

*Lemmatizes the text from a file and writes the output into another file; returns a dictionary with unknown forms and their counts*

```python
from lemmatizer import *
nondict = Lemmatizer.process_text(infile, outfile)
```

**Lemmatize all texts in the directory**

*Lemmatizes the text from all txt files in the directory and writes the output into the "lemmatized" folder; returns a dictionary with unknown forms and their counts*

```python
nondict = Lemmatizer.process_files(path)
```

**Lemmatize a string**

*Initializes the Lemmatizer class for a string*

There are two available methods for now, 'baseline' and 'predict'. 'Baseline' returns lemmas for all known words
and demutated forms for unknown words; 'predict' predicts lemmas for unknown words. The default method is 'predict'.

```python
lem = Lemmatizer(string, method='baseline')
lemmatizedString = lem.lemmaText
```

It has the following attributes:
* `lem.text` -- input string cleaned from punctuation and non-word symbols
* `lem.words` -- list of tokens
* `lem.lemmaText` -- lemmatized string 
* `lem.nondict` -- list of unknown words
* `lem.recall` -- shows the percentage of known forms in the string
* `lem.nr_tokens` -- number of tokens in a string
* `lem.nr_unique` -- number of unique tokens in a string

**Demutate a word**

*Returns a demutated word*
```python
demutatedWord = Lemmatizer.demutate(word)
```

**Predict lemmas for unknown forms**

*Takes a dictionary of OOV-words and their counts as input and creates two files for further manual revision:
OOV-words sorted by frequency higher than a given threshold (the  default one is 0) and a file with triplets of OOV-word, closest known form from the dictionary and proposed lemma. 
Returns a list of tuples.*

```python
proposed = Lemmatizer.predict_lemmas(file_for_proposed, file_for_nondict, nondict, threshold=5)
```

**Update a dictionary**

*Adds words from a preformatted file ("lemma\tform1,form2...\n") to the "forms.json" dictionary and also updates dictionaries of form and lemma probabilities*

```python
Lemmatizer.update_dict(path_to_dict, path_to_update)
```


### Evaluation

There is a test set of 50 random sentences (50\_gold\_test.txt) and a manually lemmatized gold standard (50\_gold\_lem.txt) available for evaluation.
