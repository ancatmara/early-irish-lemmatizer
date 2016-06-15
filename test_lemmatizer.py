from lemmatizer import *
from collections import Counter
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
        print('Processing %s' % (file))
        fileRecall = process_text(os.path.join(path, file), path + '\\lemmatized\\lem_' + file)
        totalRecall += fileRecall
    totalRecall = totalRecall / len(files)
    print(totalRecall)
    #totalProposed = predict_lemmas(totalUnlemmatized)
    #return totalProposed

def predict_lemmas(unlemmatized):
    unlemmatizedCounts = Counter(unlemmatized)
    edits = Edits(unlemmatizedCounts, 0)
    totalProposed = edits.proposed
    with open('proposed_gold.txt', 'w', encoding= 'utf-8') as f1, open('unlemmatized_gold.txt', 'w', encoding='utf-8') as f2:
        for entry in sorted(totalProposed):
            f1.write('%s\t%s\t%s\n' % (entry[0], entry[1], entry[2]))
        for word in sorted(unlemmatizedCounts, key=unlemmatizedCounts.get):
            f2.write('%s\t%s\n' % (word, unlemmatizedCounts[word]))
    return totalProposed

def process_text(in_path, out_path):
    with open(in_path, 'r', encoding='utf-8') as f, open(out_path, 'w', encoding='utf-8') as outfile:
        totalUnlemmatized = []
        totalRecall = 0
        cnt = 0
        for line in f:
            lem = Lemmatizer(line)
            totalUnlemmatized += lem.unlemmatized
            totalRecall += lem.recall
            cnt +=1
            outfile.write(lem.lemmaText + '\n')
    totalRecall = totalRecall / cnt
    print("Recall: %s" % (totalRecall))
    #predict_lemmas(totalUnlemmatized)
    return totalRecall

if __name__ == '__main__':
    # proposed = process_files('C:\\Users\\ahten_000\\Dropbox\\Библиотека\\Вышка\\OldIrish\\texts\\processed')
    # pp(sorted(proposed)[:25])
    process_files('C:\\Users\\ahten_000\\Dropbox\\Библиотека\\Вышка\\OldIrish\\texts\\processed')

