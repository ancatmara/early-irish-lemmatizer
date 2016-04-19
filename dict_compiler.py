import re
import json
import os, sys
from urllib.request import urlopen

def crawl_dil(path):
    base = "http://dil.ie/"
    os.makedirs(path + "\\dil", exist_ok=True)
    for i in range(1, 43346):
        print("Processing page " + str(i))
        link = base + str(i)
        content = urlopen(link)
        content = content.read()
        text = content.decode("utf-8")
        with open(path + "\\dil\\" + str(i) + ".txt", "w", encoding = "utf-8") as f:
            f.write(text)

class Entry():

    headword = '<h3.*?>((\?|\d)\s)*(.*?)</h3>'
    formae = 'Forms:\s*(.*?)</p>'
    link = 'see.*?href=\".*?\">((\?|\d)\s)*(.*?)</a>'
    alph = 'abcdefghijklmnopqrstuvwxyzáóúíéṡḟōäïāūæēṅǽüöβīḯ'
    bad_forms = ["n", "m", "f", "a", "in", "is", "na", "con", "co", "ra", "ar", "ol", "bar", "for", "far", "an", "ro", "i"]
    punctuation = " ?!,.:;†*—/\-%'$~1234567890̆ "
    prefixes = ['co', 'con', 'for', 'do', 'at', 'as', 'ad', 'ní', 'ro', 'ra', 'a', 'ar', 'ath', 'aith',
                'd', 'da', 'dan', 'der', 'derb', 'di', 'dob', 'dom', 'don', 'dot', 'é', 'fo', 'id', 'in',
                'ind', 'imm', 'm', 'mí', 'n', 'nd', 'no', 'prím', 's', 't', 'to']


    def __init__(self, file):
        self.text = file.read()
        self.forms = []
        self.lemma = ''
        self.border = ''
        self.stem = ''

    def get_forms(self):
        res_headword = re.search(self.headword, self.text)
        res_forms = re.search(self.formae, self.text)
        res_link = re.search(self.link, self.text)
        if res_headword:
            if res_forms:
                self.forms, self.lemma = self.process_forms(res_forms.group(1), res_headword.group(3))
            elif res_link and '(' not in res_link.group(3):
                self.forms, self.lemma = self.process_forms(res_headword.group(3), res_link.group(3))
            else:
                self.forms, self.lemma = self.process_forms(res_headword.group(3), res_headword.group(3))
        return self.forms, self.lemma


    def process_forms(self, forms, lemma):
        """
        :param forms: string with forms
        :param lemma: string with lemmas
        """
        self.lemma = lemma.split(",")[0].strip(self.punctuation)
        if '(?) ' in self.lemma:
            self.lemma = self.lemma[self.lemma.index(" ")+1:]
        if self.lemma not in self.prefixes:
            self.forms = forms.split(",") + lemma.split(",")
            self.forms = [form.strip("1234567890?†* ") for form in self.forms]
            self.forms = self.remove_junk()
            self.forms = [form for form in self.forms if len(form) != 0]
            for form in self.forms:
                form = self.check_brackets(form)
            self.border = self.find_border()
            self.stem = self.find_stem()
            for form in self.forms:
                self.normalize(form)
            self.forms = [form for form in self.forms if len(form) > 0 and form[0] != "-"]
            self.forms = [form.strip(self.punctuation) for form in self.forms]
        else:
            pass
        return self.forms, self.lemma

    def remove_junk(self):
            """
            :return: a list of forms without junk like zero-length forms and hardly restorable
            variations in the middle of the form ("-rrt(h)-" etc.)
            """
            for form in self.forms:
                if len(form) != 0:
                    if len(form) == 1 and form in self.punctuation:
                        self.forms.pop(self.forms.index(form))
                    elif form[0] == "-" and form[-1] == "-":
                        self.forms.pop(self.forms.index(form))
                    elif form[-1] == "." and len(form) <= 3:
                        self.forms.pop(self.forms.index(form))
                    elif form in self.bad_forms:
                        self.forms.pop(self.forms.index(form))
                    elif form[0] == '(' and form[-1] == ')':
                        self.forms.pop(self.forms.index(form))
                else:
                    self.forms.pop(self.forms.index(form))
            return self.forms

    def check_brackets(self, form):
        """
        Checks if there are multiple variants of the form indicated by "()" and makes
        two different forms from one form with brackets
        """
        if "(" in form and ")" in form:
            i = form.index("(")
            j = form.index(")")
            extraForm = form[:i] + form[i+1:j] + form[j+1:]
            newForm = form[:i] + form[j+1:]
            self.forms.append(extraForm)
            self.forms.append(newForm)
        elif "[" in form and "]" in form:
            i = form.index("[")
            j = form.index("]")
            extraForm = form[:i] + form[i+1:j] + form[j+1:]
            newForm = form[:i] + form[j+1:]
            self.forms.append(extraForm)
            self.forms.append(newForm)

    def find_border(self):
        for form in self.forms:
            if len(form) >=2 and form[0] == "-":
                self.border = form[1]
                break
        return self.border

    def find_stem(self):
        if len(self.forms) > 1:
            for form in self.forms:
                if len(form) > 1:
                    if form[0] != '-' and self.border != '' and self.border in form:
                        parts = form.split(self.border)
                        self.stem = self.border.join(parts[:-1])
                        break
                    elif form[0] != '-' and self.border != '' and self.border in self.lemma:
                        parts = self.lemma.split(self.border)
                        self.stem = self.border.join(parts[:-1])
                        break
        else:
            self.stem = self.lemma
        return self.stem

    def normalize(self, form):
        """Normalizes contracted forms"""
        try:
            if len(form) >= 2 and form[0] == "-":
                if self.stem[-1] == 'i' and self.border in ['l', 'm', 'n', 'r']:
                    form = self.stem[:-1] + form[1:]
                    self.forms.append(form)
                else:
                    form = self.stem + form[1:]
                    self.forms.append(form)
        except IndexError:
            pass

    def make_dict(self, words):
        self.lemma = self.lemma.lower()
        for form in self.forms:
            form = form.lower()
            if len(form) != 0 and form not in self.punctuation and form not in self.bad_forms:
                if form not in words.keys():
                    words[form] = (self.lemma,)
                if self.lemma not in words.keys():
                    words[self.lemma] = (self.lemma,)
                else:
                    if self.lemma not in words[form]:
                        words[form] += (self.lemma,)
        for k, v in words.items():
            if len(v) == 0:
                words[k] = k
        words = {k:words[k] for k in words if len(k) != 0}
        return words

def write_data(words):
    with open("forms.json", "w", encoding = "utf-8") as f1:
        json.dump(words, f1, sort_keys = True, ensure_ascii = False)

if __name__ == '__main__':
    crawl_dil(sys.argv[1])
    words = {}
    for root, dirs, files in os.walk(sys.argv[1] + "\\dil"):
        for name in files:
            print("Processing " + name)
            file = open(os.path.join(root, name), "r", encoding = "utf-8")
            entry = Entry(file)
            forms, lemma = entry.get_forms()
            words = entry.make_dict(words)
        write_data(words)
