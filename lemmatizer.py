class Lemmatizer():
    punkt = ',…—\–()[].!?:﻿;\'‘’"„“«»*-'
    mutations = {'bh': 'b', 'mb': 'b', 'ch': 'c', 'gc': 'c', 'gh': 'g', 'ng': 'g', 'dh': 'd', 'nd': 'd', 'fh': 'f',
                 'ḟ': 'f', 'ḟh': 'f', 'bhf': 'f', 'mm': 'm', 'll': 'l', 'nn': 'n', 'ph': 'p', 'bp': 'p', 'rr': 'r',
                 'sh': 's', 'ṡ': 's', 'th': 't', 'dt': 't', 'he': 'e', 'hé': 'é', 'ha': 'a', 'há': 'á', 'hi': 'i',
                 'hí': 'í', 'ho': 'o', 'hó': 'ó', 'hu': 'u', 'hú': 'ú', 'n-': '', 'h-': '', 'ss': 's', 'ts': 's'}
    with open("forms_new.json", encoding='utf-8') as f:
        lemmadict = json.loads(f.read())

    def __init__(self, text):
        self.text, self.words = self.preprocess(text)
        self.lemmaText, self.counts = self.make_lemmatized_text()
        self.accuracy = self.metrics()
        self.unlemmatized = self.show_unlemmatized()

    def preprocess(self, text):
        """
        Normalizes input text
        :param text: str
        :return: normalized text and a list of words
        """
        self.words = text.lower().split()
        self.words = [word.strip(self.punkt) for word in self.words]
        self.words = [word for word in self.words if len(word) != 0]
        self.text = " ".join(self.words)
        return self.text, self.words

    def demutate(self, word):
        """
        Checks if the word is lenited, nasalized etc. and restores  its original form
        :param word: str
        :return: str
        """
        if word[:2] in self.mutations:
            word = self.mutations[word[:2]] + word[2:]
        elif word[0] in self.mutations:
            word = self.mutations[word[0]] + word[1:]
        return word

    def lemmatize(self, word):
        """
        Searches for the word's lemma in the precompiled dictionary.
        If it cannot be found, lemma value is set to None.
        :param word: str
        :return: a tuple (word, lemma) if there is only one possible lemma
                 a tuple (word, (lemma, lemma, lemma...)) if there are several possible lemmas
        """
        word = word.strip(self.punkt)
        if word in self.lemmadict:
            res = (word, tuple(self.lemmadict[word]))
        elif self.demutate(word) in self.lemmadict:
            res = (self.demutate(word), tuple(self.lemmadict[self.demutate(word)]))
        else:
            res = (word, None)
        return res

    def count(self, res):
        """
        Makes a word frequency dict
        :param res: a (word, lemma) tuple
        :return: dict
        """
        if res in self.counts:
            self.counts[res] += 1
        else:
            self.counts[res] = 1
        return self.counts

    def make_lemmatized_text(self):
        """
        Makes a lemmatized text and counts (word, lemma) frequency
        :return: a lemmatized text (str),
                {(word, lemma) : count}
        """
        self.lemmaText = ''
        self.counts = {}
        for word in self.words:
            res = self.lemmatize(word)
            if type(res[-1]) == str:
                self.lemmaText += res[-1] + ' '
            elif type(res[-1]) == tuple:
                self.lemmaText += res[-1][0] + ' '
            else:
                self.lemmaText += res[0] + ' '
            self.counts = self.count(res)
        return self.lemmaText, self.counts

    def show_unlemmatized(self):
        """
        :return: a set of non-lemmatizzed words
        """
        self.unlemmatized = set()
        for key in self.counts.keys():
            if key[-1] is None:
                self.unlemmatized.add(key[0])
        return self.unlemmatized

    def metrics(self):
        """
        :return: accuracy (a float < 1)
        """
        self.cntLemmatized = 0
        for key in self.counts.keys():
            if key[-1] is not None:
                self.cntLemmatized += self.counts[key]
        try:
            self.accuracy = self.cntLemmatized / len(self.words)
        except ZeroDivisionError:
            self.accuracy = 0
        return self.accuracy


def process_files(path):
    """
    Lemmatizes texts from all the files in a given directory and puts lemmatized texts in a new folder.
    Counts average accuracy
    :param path: path to files
    :return: average accuracy (a float < 1)
    """
    totalAccuracy = 0
    os.makedirs(path + "\\lemmatized", exist_ok=True)
    files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
    for file in files:
        with open(os.path.join(path, file), 'r', encoding='utf-8') as infile:
            lem = Lemmatizer(infile.read())
            totalAccuracy += lem.accuracy
        with open(path + '\\lemmatized\\lem_' + file, 'w', encoding='utf-8') as outfile:
            outfile.write(lem.lemmaText)
    totalAccuracy = totalAccuracy / len(files)
    return totalAccuracy


if __name__ == '__main__':
    import os
    import sys
    import json
    print(process_files(sys.argv[1]))

