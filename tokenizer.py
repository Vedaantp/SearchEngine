from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from nltk import ngrams
import re
import json
import csv
import math

stemmer = PorterStemmer()
word_weights = {}
word_frequency = {}
total_tokens = 0
doc_num = 0
indexes = {}

def join_stems(tokens):
    new_tokens = []

    for token in tokens:
        new_tokens.append(' '.join(token))

    return new_tokens

def stemming(tokens):
    global stemmer

    new_tokens = []

    for word in tokens:
        new_tokens.append(stemmer.stem(word))

    return new_tokens

def weights(tokens, weight):
    global word_weights

    for word in tokens:
        # word = stemmer.stem(word)
        if word not in word_weights:
            word_weights[word] = weight
        else:
            word_weights[word] += weight
        
    return

def frequencies(tokens):
    global word_frequency
    # global stemmer

    for word in tokens:
        # word = stemmer.stem(word)
        if word not in word_frequency:
            word_frequency[word] = 1
        else:
            word_frequency[word] += 1

    return

def removeEscapeSequences(text):
    escape_sequence_pattern = r'(\\[ntrufUxX\d]{1,5}|\\u[0-9a-fA-F]{4}|[\']|[\"])'

    return re.sub(escape_sequence_pattern, '', text)

def grabContent(tag, soup):
    content = soup.find_all([tag])
    pure = []
    for c in content:
        pure.append(c.get_text())

    return(pure)

def index_dump(path):
    global indexes

    flat_data = []
    for key, values in indexes.items():
        doc_freq = values["doc_freq"]
        for url, doc_info in values["docs"].items():
            row = [key, doc_freq, url, doc_info["frequency"], doc_info["weight"], doc_info["tf_idf"], doc_info['file']]
            flat_data.append(row)

    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Doc_Freq", "URL", "Frequency", "Weight", "TF_IDF", 'File'])
        writer.writerows(flat_data)

    return

def index(url, text_data):
    global word_weights
    global word_frequency
    global indexes



    for key, value in word_weights.items():

        if key not in indexes:
            indexes[key] = {'doc_freq': 1, 'docs': {}}

        else:
            indexes[key]['doc_freq'] += 1

        if url not in indexes[key]['docs']:
            # indexes[key]['docs'][url] = {"total_tokens": total_tokens, "frequency": word_frequency.get(key, 0), "weight": value, "tf_idf": (word_frequency.get(key, 0) / total_tokens)}
            indexes[key]['docs'][url] = {"total_tokens": total_tokens, "frequency": word_frequency.get(key, 0), "weight": value, "tf_idf": (1 + math.log10(word_frequency.get(key, 0))), 'file': text_data}


def tokenizing(soup, url, worker_num, text_data):
    global word_weights
    global word_frequency
    global total_tokens
    global doc_num
    global indexes

    total_tokens = 0
    unique_tokens = 0
    content_type = ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'body', 'p', 'b', 'i', 'u']
    content_text = []
    content_tokens = []
    n_grams_tokens = []
    pattern = r"[a-zA-Z0-9]{2,}"
    tokenizer = RegexpTokenizer(pattern)
    
    for types in content_type:
        content_text.append(removeEscapeSequences(' '.join(grabContent(types, soup))))

    for text in content_text:
        content_tokens.append(stemming(tokenizer.tokenize(text)))

    for i in range(len(content_tokens)):
        temp1 = join_stems(list(ngrams(content_tokens[i], 2)))
        temp2 = join_stems(list(ngrams(content_tokens[i], 3)))

        n_grams_tokens.append(temp1)
        n_grams_tokens.append(temp2)

        weight = 0

        if i == 0:
            weight = 150

        elif i == 1:
            weight = 125

        elif i == 2:
            weight = 120

        elif i == 3:
            weight = 115

        elif i == 4:
            weight = 110

        elif i == 5:
            weight = 100

        elif i == 6:
            weight = 90

        elif i == 7:
            weight = 40

        elif i == 8:
            weight = 40

        elif i == 9:
            weight = 40

        elif i == 10:
            weight = 35

        elif i == 11:
            weight = 10

        elif i == 12:
            weight = 10
            
        frequencies(content_tokens[i])
        frequencies(temp1)
        frequencies(temp2)
        weights(content_tokens[i], weight)
        weights(temp1, weight)
        weights(temp2, weight)

    for n_gram in n_grams_tokens:
        content_tokens.append(n_gram)

    for tokens in content_tokens:
        total_tokens += len(tokens)
        unique_tokens += len(set(tokens))

    index(url, text_data)

    word_weights = {}
    word_frequency = {}

    return unique_tokens
