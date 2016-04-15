from lemmatizer import *
from collections import OrderedDict
from pprint import pprint as pp
import os

def process_files(path):
    """
    Lemmatizes texts from all the files in a given directory and puts lemmatized texts in a new folder.
    Counts average accuracy
    :param path: path to files
    :return: average accuracy (a float < 1)
    """
    totalRecall = 0
    totalUnlemmatized = []
    os.makedirs(path + "\\lemmatized", exist_ok=True)
    files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
    for file in files:
        with open(os.path.join(path, file), 'r', encoding='utf-8') as infile:
            lem = Lemmatizer(infile.read())
            totalUnlemmatized += lem.unlemmatized
            totalRecall += lem.recall
            print("Recall in %s: %s" % (file, lem.recall))
        with open(path + '\\lemmatized\\lem_' + file, 'w', encoding='utf-8') as outfile:
            outfile.write(lem.lemmaText)
    with open('test_unlemmatized.txt', 'w', encoding='utf-8') as f:
        for word in sorted(totalUnlemmatized):
            f.write(word + '\n')
    totalRecall = totalRecall / len(files)
    print(totalRecall)

    unlemmatizedCounts = Lemmatizer.count_unlemmatized(totalUnlemmatized)
    edits = Edits(unlemmatizedCounts)
    totalProposed = edits.proposed
    with open('test_proposed_lemmas.txt', 'w', encoding= 'utf-8') as f1:
        for entry in sorted(totalProposed):
            f1.write(entry + '\n')
    return totalRecall, totalProposed


if __name__ == '__main__':
    totalRecall, proposed = process_files("C:\\Users\\ahten_000\\Dropbox\\Библиотека\\Вышка\\OldIrish\\texts\\test")
    # pp(sorted(proposed)[:25])
