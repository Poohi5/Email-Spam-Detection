import sys
import glob
import errno
import csv
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

def preprocess(text):
    set(stopwords.words('english'))

    stop_words = set(stopwords.words('english'))

    word_tokens = word_tokenize(text)

    words_list = []
    for w in word_tokens:
        if w not in stop_words:
            words_list.append(w)

    Stem_words = []
    ps =PorterStemmer()
    for w in words_list:
        rootWord=ps.stem(w)
        Stem_words.append(rootWord)
#    print(words_list)
#    print(Stem_words)
    text = ' '.join(word for word in Stem_words)
    return text

def clean_text(text):
    # remove urls
    text = re.sub(r'http\S+', ' ', text)
    # or replace urls with word httpaddress
    # text = re.sub('(http|https)://[^\s]*', 'httpaddress', text)

    # replace email address with word emailaddress
    text = re.sub('[^\s]+@[^\s]+', ' ', text)

    # replace "$" with word "dollar".
    text = re.sub('[$]+', 'dollar', text)

    # remove numbers
    #text = re.sub("\d+", ' ', text)
    # or replace numbers with word number
    text = re.sub('[0-9]+', '', text)

    # remove html tags
    text = re.sub('<[^<>]+>', ' ', text)
    # remove new lines
    text = text.replace('\\n', '')
    text = text.replace('\\r', '')
    text = text.replace('\\t', '')
    text = text.replace('To:', '')
    text = text.replace('From:', '')
    text = text.replace('Subject:', '')
    text = text.replace('"','')
    text = text.replace('-', '')
    text = text.replace('_', '')
    text = text.replace('/', '')
    text = text.replace('?', '')
    text = text.replace('~', '')
    text = text.replace('<', '')
    text = text.replace(':', '')
    text = text.replace('original message', '')
    text = text.replace('href', '')
    text = text.replace('http', '')
    text = text[1:]
    # remove punctuations
    for ch in string.punctuation:
        text = text.replace(ch, '')
    text = text.lower()
    #text = text.replace('rn', ' ')
    return text


path = './ham/*.txt'
files = glob.glob(path)
mat = []
ls = []
#i=0
for name in files: # 'file' is a builtin type, 'name' is a less-ambiguous variable name.
    try:
        with open(name, 'rb') as f: # No need to specify 'r': this is the default.
            ls = []
            #ls.append(i)
            #print(str(f.readlines()))
            text = f.read()
            text = str(text)
            text = clean_text(text.replace('\n', ''))
            text = preprocess(text)
            ls.append(text)
            ls.append("0")
    except IOError as exc:
        if exc.errno != errno.EISDIR: # Do not fail if a directory is found, just ignore it.
            raise # Propagate other kinds of IOError.
    #i+=1
    mat.append(ls)

print(mat[5])
print(len(mat))

fields = ['email', 'class']

filename="./ham_csv.csv"
with open(filename, 'w') as csvfile:
    # creating a csv writer object
    csvwriter = csv.writer(csvfile)

    # writing the fields
    csvwriter.writerow(fields)

    # writing the data rows
    #for row in mat:
    csvwriter.writerows(mat)

