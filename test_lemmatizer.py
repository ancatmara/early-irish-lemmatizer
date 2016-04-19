from lemmatizer import *
from collections import OrderedDict
from pprint import pprint as pp
import os, sys

def process_files(path):
    """
    Lemmatizes texts from all the files in a given directory and puts lemmatized texts in a new folder.
    Writes proposed lemmas for unknown words into a file.
    Counts average recall.
    :param path: path to files
    :return: a list of (OOV form, closest form from lemmadict, lemma) tuples
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
    totalRecall = totalRecall / len(files)
    print(totalRecall)

    unlemmatizedCounts = Lemmatizer.count_unlemmatized(totalUnlemmatized)
    edits = Edits(unlemmatizedCounts, 1)
    totalProposed = edits.proposed
    with open('proposed_lemmas.txt', 'w', encoding= 'utf-8') as f1, open('unlemmatized.txt', 'w', encoding='utf-8') as f2:
        for entry in sorted(totalProposed):
            f1.write('%s\t%s\t%s\n' % (entry[0], entry[1], entry[2]))
        for word in sorted(unlemmatizedCounts, key=unlemmatizedCounts.get):
            f2.write('%s\t%s\n' % (word, unlemmatizedCounts[word]))
    return totalProposed


if __name__ == '__main__':
    proposed = process_files(sys.argv[1])
    # pp(sorted(proposed)[:25])
