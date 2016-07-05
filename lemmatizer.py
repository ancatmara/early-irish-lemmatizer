import json
import re
import os
from collections import Counter

class Lemmatizer():

    punkt = ',…—\–()[].!?:﻿;\'‘’"„“«»*-'
    mutations = {'bh': 'b', 'mb': 'b', 'ch': 'c', 'gc': 'c', 'gh': 'g', 'ng': 'g', 'dh': 'd', 'nd': 'd', 'fh': 'f',
                 'ḟ': 'f', 'ḟh': 'f', 'bhf': 'f', 'mm': 'm', 'll': 'l', 'nn': 'n', 'ph': 'p', 'bp': 'p', 'rr': 'r',
                 'sh': 's', 'ṡ': 's', 'th': 't', 'dt': 't', 'he': 'e', 'hé': 'é', 'ha': 'a', 'há': 'á', 'hi': 'i',
                 'hí': 'í', 'ho': 'o', 'hó': 'ó', 'hu': 'u', 'hú': 'ú', 'n-': '', 'h-': '', 'ss': 's', 'ts': 's',
                 'n': 'e', 'né': 'é', 'na': 'a', 'ná': 'á', 'ni': 'i', 'ní': 'í', 'no': 'o', 'nó': 'ó', 'nu': 'u',
                 'nú': 'ú', 'm-': '', 't-': '', 't\'': ' ', 'm\'': '', 'd\'': '', 'l-': '', 'mh': 'm', 'r-': '',
                 's-': '', 'cc': 'c', 'mh\'': ''}

    with open("./dicts/forms.json", encoding='utf-8') as f, open("./dicts/word_probs.json", encoding="utf-8") as f1,\
        open("./dicts/lemma_probs.json", encoding="utf-8") as f2:
        lemmadict = json.loads(f.read())
        wordModel = json.loads(f1.read())
        lemmaModel = json.loads(f2.read())

    def __init__(self, text, method = 'predict'):
        self.text, self.words = self.preprocess(text)
        self.lemmaText, self.nondict, self.cnt = self.make_lemmatized_text(method)
        self.recall = self.compute_recall()
        self.nr_tokens = len(self.words)
        self.nr_unique = len(set(self.words))
        self.method = method

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

    def make_lemmatized_text(self, method):
        """
        Makes a lemmatized text and counts (word, lemma) frequency
        :return: a lemmatized text (str),
                {(word, lemma) : count}
        """
        self.lemmaText = ''
        self.nondict = []
        self.cnt = 0
        for word in self.words:
            res = self.lemmatize(word)
            if res[-1] is None:
                self.unknown_words(res[0], method)
            else:
                self.cnt += 1
                if len(res[-1]) == 1:
                    self.lemmaText += res[-1][0] + ' '
                elif len(res[-1]) > 1:
                    candidates = [element for element in res[-1]]
                    try:
                        bestLemma = max(candidates, key = Lemmatizer.lemmaModel.get)
                        self.lemmaText += bestLemma + ' '
                    except TypeError:
                        self.lemmaText += res[-1][0] + ' '
        return self.lemmaText, self.nondict, self.cnt

    def unknown_words(self, word, method):
        if method == 'baseline':
            self.lemmaText += self.demutate(word) + ' '
        if method == 'predict':
            closest = Edits.correct(Lemmatizer.demutate(word))
            if closest is not None:
                try:
                    predictedLemma = max(Lemmatizer.lemmadict[closest], key=Lemmatizer.lemmaModel.get)
                    self.lemmaText += predictedLemma + ' '
                except TypeError:
                        self.lemmaText += Lemmatizer.lemmadict[closest][0] + ' '
            else:
                self.lemmaText += self.demutate(word) + ' '
        self.nondict.append(self.demutate(word))


    def compute_recall(self):
        """
        :return: recall score
        """
        try:
            self.recall = self.cnt / len(self.words)
        except ZeroDivisionError:
            self.recall = 0
        return self.recall

    @staticmethod
    def update_dict(path_to_dict, path_to_update):
        """
        Adds words from a file ("lemma\tform1,form2...\n") to the dictionary
        :param path_to_update: path to txt/csv file with words to add
        :param path_to_dict: path to a dictionary file in json
        """
        with open(path_to_update, 'r', encoding='utf-8') as f, open(path_to_dict, encoding='utf-8') as f1:
            lemmadict = json.loads(f1.read())
            for line in f:
                res = re.search('(.+)\t(.+)\n', line)
                if res:
                    lemma = res.group(1)
                    forms = set(res.group(2).lower().split(','))
                    for form in forms:
                        if form in lemmadict.keys():
                            lemmadict[form] += (lemma,)
                        else:
                            lemmadict[form] = (lemma,)
        with open("forms.json", "w", encoding = "utf-8") as f1:
            json.dump(lemmadict, f1, sort_keys = True, ensure_ascii = False)

    @staticmethod
    def predict_lemmas(file1, file2, unlemmatizedCounts, threshold=0):
        """
        Predicts lemmas for unlemmatized words.
        :param file1: path to file to write unlemmatized word, the closest dictionary form and predicted lemma(s)
        :param file2: path to file to write unlemmatized words with their counts
        :param unlemmatizedCounts: a dict with unlemmatized words and their counts
        :param threshold: minimal frequency of unlemmatized word
        :return: a list of (OOV form, closest form from lemmadict, lemma) tuples
        """
        edits = Edits(unlemmatizedCounts, threshold)
        totalProposed = edits.proposed
        with open(file1, 'w', encoding= 'utf-8') as f1, open(file2, 'w', encoding='utf-8') as f2:
            for entry in sorted(totalProposed):
                f1.write('%s\t%s\t%s\n' % (entry[0], entry[1], entry[2]))
            for word in sorted(unlemmatizedCounts, key=unlemmatizedCounts.get):
                f2.write('%s\t%s\n' % (word, unlemmatizedCounts[word]))
        return totalProposed

    @staticmethod
    def process_text(in_path, out_path):
        """
        Processes text in a file
        :param in_path: path to txt file
        :param out_path: path to file with lemmatized text
        """
        with open(in_path, 'r', encoding='utf-8') as f, open(out_path, 'w', encoding='utf-8') as outfile:
            unlemmatized = []
            for line in f:
                lem = Lemmatizer(line)
                unlemmatized += lem.nondict
                outfile.write(lem.lemmaText + '\n')
        return Counter(unlemmatized)

    @staticmethod
    def process_files(path):
        """
        Lemmatizes texts from all the files in a given directory and puts lemmatized texts in a new folder.
        Writes proposed lemmas for unknown words into a file.
        Counts average recall.
        :param path: path to files
        :return: a list of (OOV form, closest form from lemmadict, lemma) tuples
        """
        totalUnlemmatized = Counter()
        os.makedirs(path + "/lemmatized", exist_ok=True)
        files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
        for file in files:
            print('Processing %s' % (file))
            fileUnlemmatized = Lemmatizer.process_text(os.path.join(path, file), path + '/lemmatized/lem_' + file)
            totalUnlemmatized += fileUnlemmatized
        return totalUnlemmatized


# todo add function for updating word and lemma probs!


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

    @staticmethod
    def edits1(word):
       splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
       deletes = [a + b[1:] for a, b in splits if b]
       transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
       replaces = [a + c + b[1:] for a, b in splits for c in Edits.alphabet if b]
       inserts = [a + c + b for a, b in splits for c in Edits.alphabet]
       return set(deletes + transposes + replaces + inserts)

    @staticmethod
    def known_edits2(word):
        return set(e2 for e1 in Edits.edits1(word) for e2 in Edits.edits1(e1) if e2 in Lemmatizer.wordModel.keys())

    @staticmethod
    def known(words): return set(w for w in words if w in Lemmatizer.wordModel.keys())

    @staticmethod
    def correct(word):
        candidates = Edits.known(Edits.edits1(word)) or Edits.known_edits2(word)
        candidates = [c for c in candidates if c[0] in Edits.vowels and word[0] in Edits.vowels \
                      or word[0] in Edits.consonants and word[0] == c[0]]
        if len(candidates) != 0:
            corr = max(candidates, key = Lemmatizer.wordModel.get)
        else:
            corr = None
        return corr
