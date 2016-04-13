from lemmatizer import *
from pprint import pprint as pp
import os
import sys

def process_files(path):
    """
    Lemmatizes texts from all the files in a given directory and puts lemmatized texts in a new folder.
    Writes proposed lemmas for unknown words into a file.
	Counts average recall. 
    :param path: path to files
    :return: average recall
    """
    totalRecall = 0
    totalUnlemmatized = []
    totalProposed = []
    os.makedirs(path + "\\lemmatized", exist_ok=True)
    files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
    for file in files:
        with open(os.path.join(path, file), 'r', encoding='utf-8') as infile:
            lem = Lemmatizer(infile.read())
            edits = Edits(lem.unlemmatized)
            totalRecall += lem.recall
            totalProposed += edits.proposed
            print("Recall in %s: %s" % (file, lem.recall))
            totalUnlemmatized += lem.unlemmatized
        with open(path + '\\lemmatized\\lem_' + file, 'w', encoding='utf-8') as outfile:
            outfile.write(lem.lemmaText)
        with open('unlemmatized.txt', 'w', encoding='utf-8') as f:
            for word in sorted(set(totalUnlemmatized)):
                f.write(word + '\n')
        with open('proposed_lemmas.txt', 'w', encoding= 'utf-8') as f1:
            for entry in sorted(totalProposed):
                f1.write(entry + '\n')
    totalRecall = totalRecall / len(files)
    return totalRecall, totalProposed


if __name__ == '__main__':
    totalRecall, proposed = process_files(sys.argv[1])
    pp(sorted(proposed)[:25])
