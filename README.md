# Early Irish Lemmatizer

There are two "editions" of the lemmatizer:

* rule-based (as in good old days)
* seq2seq (fancy neural network stuff)

They are absolutely independent, so you are free to choose whichever you like; both are ready-to-use. 

### Rule-based

This version is based on the [eDIL](http://dil.ie/). It shows ca. 80% accuracy on texts that follow classical Old Irish orthography, but performs poorly on Middle and Early Modern Irish texts. The algorithm does not resolve all possible cases of spelling variation and the lexicon does not cover all the inflectional forms. Please keep in mind that it is just a study project.

### Seq2seq

This version is also trained on the eDIL, but it yields more promising results: 99.2 % accuracy for known words and 64.9 % for unknown words. A detailed English description of neural network architecture and evalution can be found in my MA thesis (full text [here](https://www.academia.edu/35596032/Morphological_analysis_of_Old_Irish_data_with_neural_networks)).
