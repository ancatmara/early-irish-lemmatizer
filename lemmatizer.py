import json
import re

class Lemmatizer():

    punkt = ',…—\–()[].!?:﻿;\'‘’"„“«»*-'
    mutations = {'bh': 'b', 'mb': 'b', 'ch': 'c', 'gc': 'c', 'gh': 'g', 'ng': 'g', 'dh': 'd', 'nd': 'd', 'fh': 'f',
                 'ḟ': 'f', 'ḟh': 'f', 'bhf': 'f', 'mm': 'm', 'll': 'l', 'nn': 'n', 'ph': 'p', 'bp': 'p', 'rr': 'r',
                 'sh': 's', 'ṡ': 's', 'th': 't', 'dt': 't', 'he': 'e', 'hé': 'é', 'ha': 'a', 'há': 'á', 'hi': 'i',
                 'hí': 'í', 'ho': 'o', 'hó': 'ó', 'hu': 'u', 'hú': 'ú', 'n-': '', 'h-': '', 'ss': 's', 'ts': 's',
                 'n': 'e', 'né': 'é', 'na': 'a', 'ná': 'á', 'ni': 'i', 'ní': 'í', 'no': 'o', 'nó': 'ó', 'nu': 'u',
                 'nú': 'ú', 'm-': '', 't-': '', 't\'': ' ', 'm\'': '', 'd\'': ''}

    with open(".\\dicts\\forms.json", encoding='utf-8') as f, open(".\\dicts\\word_probs.json", encoding="utf-8") as f1,\
        open(".\\dicts\\lemma_probs.json", encoding="utf-8") as f2:
        lemmadict = json.loads(f.read())
        wordModel = json.loads(f1.read())
        lemmaModel = json.loads(f2.read())

    def __init__(self, text):
        self.text, self.words = self.preprocess(text)
        self.lemmaText, self.unlemmatized, self.cnt = self.make_lemmatized_text()
        self.accuracy = self.metrics()
        self.nr_tokens = len(self.words)
        self.nr_unique = len(set(self.words))

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

    @staticmethod
    def demutate(word):
        """
        Checks if the word is lenited, nasalized etc. and restores  its original form
        :param word: str
        :return: str
        """
        if len(word) != 0:
            if word[:2] in Lemmatizer.mutations:
                word = Lemmatizer.mutations[word[:2]] + word[2:]
            elif word[0] in Lemmatizer.mutations:
                word = Lemmatizer.mutations[word[0]] + word[1:]
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

    def make_lemmatized_text(self):
        """
        Makes a lemmatized text and counts (word, lemma) frequency
        :return: a lemmatized text (str),
                {(word, lemma) : count}
        """
        self.lemmaText = ''
        self.unlemmatized = []
        self.cnt = 0
        for word in self.words:
            res = self.lemmatize(word)
            if res[-1] is None:
                self.lemmaText += res[0] + ' '
                self.unlemmatized.append(res[0])
            else:
                self.cnt += 1
                if len(res[-1]) == 1:
                    self.lemmaText += res[-1][0] + ' '
                elif len(res[-1]) > 1:
                    candidates = [element for element in res[-1]]
                    bestLemma = max(candidates, key = Lemmatizer.lemmaModel.get)
                    self.lemmaText += bestLemma + ' '
        return self.lemmaText, self.unlemmatized, self.cnt

    def metrics(self):
        """
        :return: recall score
        """
        try:
            self.recall = self.cnt / len(self.words)
        except ZeroDivisionError:
            self.recall = 0
        return self.recall

    def update_dict(self, path):
        """
        Adds words from a file ("lemma\tform1,form2...\n") to the dictionary
        :param path: path to txt/csv file with words to add
        """
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                res = re.search('(.+)\t(.+)\n', line)
                if res:
                    lemma = res.group(1)
                    forms = set(res.group(2).lower().split(','))
                    for form in forms:
                        if form in self.lemmadict.keys():
                            self.lemmadict[form] += (lemma,)
                        else:
                            self.lemmadict[form] = (lemma,)
        with open(".\\dicts\\forms.json", "w", encoding = "utf-8") as f1:
            json.dump(self.lemmadict, f1, sort_keys = True, ensure_ascii = False)


class Edits():
    alphabet = 'abcdefghijklmnopqrstuvwxyzáóúíéṡḟōäïāūæēṅǽüöβīḯ'
    vowels = 'aeiouvyáóúíéōäāïūæēǽüöīḯ'
    consonants = 'bcdfghjklmnpqrstvwxzṡḟṅβ'

    def __init__(self, unlemmatized, threshold = 0):
        self.threshold = threshold
        self.unlemmatized = unlemmatized
        self.filteredUnlemmatized = self.filter_unlemmatized()
        self.proposed = self.levenshtein_unknown()

    def filter_unlemmatized(self):
        self.filteredUnlemmatized = []
        [self.filteredUnlemmatized.append(key) for key, value in self.unlemmatized.items() if value > self.threshold]
        return self.filteredUnlemmatized

    def levenshtein_unknown(self):
        self.proposed = []
        for word in self.filteredUnlemmatized:
            closest = self.correct(Lemmatizer.demutate(word))
            if closest is not None:
                entry = (Lemmatizer.demutate(word), closest, (Lemmatizer.lemmadict[closest]))
                self.proposed.append(entry)
        return self.proposed

    def edits1(self, word):
       splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
       deletes = [a + b[1:] for a, b in splits if b]
       transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
       replaces = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
       inserts = [a + c + b for a, b in splits for c in self.alphabet]
       return set(deletes + transposes + replaces + inserts)

    def known_edits2(self, word):
        return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in Lemmatizer.wordModel.keys())

    def known(self, words): return set(w for w in words if w in Lemmatizer.wordModel.keys())

    def correct(self, word):
        candidates = self.known(self.edits1(word)) or self.known_edits2(word)
        candidates = [c for c in candidates if c[0] in self.vowels and word[0] in self.vowels \
                      or word[0] in self.consonants and word[0] == c[0]]
        if len(candidates) != 0:
            corr = max(candidates, key = Lemmatizer.wordModel.get)
        else:
            corr = None
        return corr