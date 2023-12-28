from nltk import ngrams
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import json
import math
import timeit


def openIndexFiles():

    with open('indexPos/index_positions.json', 'r') as f:
        index_pos = json.load(f)

    print("Index Loaded")
    
    return index_pos


def normalize_vector(vector):

    magnitude = math.sqrt(sum(float(x)**2 for x in vector))
    normalized_vector = [float(x) / magnitude for x in vector]

    return normalized_vector


def searchQueryUIFlask(query, index_pos):

    try:
        request = tokenizeQuery(query)

        if len(request) > 0:
            matching = matching_main(request, index_pos)
            ranks = ranking(matching)
            top_five = resultsOutput(ranks)

            return top_five
        
        else:
            print("Please enter a proper search query")

    except Exception as e:
        print(f"An error has occurred {e}")


def tokenizeQuery(query):

    pattern = r"[a-zA-Z0-9]{2,}"
    tokenizer = RegexpTokenizer(pattern)
    stemmer = PorterStemmer()

    tokens = [stemmer.stem(word) for word in tokenizer.tokenize(query)]
    bigrams = [' '.join(token) for token in ngrams(tokens, 2)]
    trigrams = [' '.join(token) for token in ngrams(tokens, 3)]
    # full_query = ' '.join(tokens)

    if len(tokens) <= 2:
        return bigrams + tokens

    return bigrams + trigrams if len(bigrams + trigrams) > 0 else tokens
    # return tokens + bigrams + trigrams


def matching_main(queries, index_pos):
    file = 'merged/sorted.csv'
    q_set = set(queries)
    data = {}
    url_scores = {}
    q_vector = []
    counter = 0

    start = timeit.default_timer()
    for query in q_set:
        matching_worker(query, file, index_pos, queries, data, q_vector, counter)
        counter += 1
    end = timeit.default_timer()
    res = end - start
    print("Searching time: ", res)

    start = timeit.default_timer()
    for key, value in data.items():
        for i in range(len(q_vector) - len(value['tf_idf'])):
            value['tf_idf'].append(0)

        dot_product = sum(float(a) * float(b) for a, b in zip(value['tf_idf'], q_vector))
        normalized_doc = normalize_vector(value['tf_idf'])
        normalized_query = normalize_vector(q_vector)
        normalized_dot_product = sum(float(a) * float(b) for a, b in zip(normalized_doc, normalized_query))
        score = float(dot_product / normalized_dot_product) if normalized_dot_product != 0 else 0.0
        score = (score * value['weight']) / 2
        url_scores[key] = (score, value['file'])

    end = timeit.default_timer()
    res = end - start
    print("Working time: ", res)

    return url_scores

def matching_worker(query, file, index_pos, queries, data, q_vector, counter):
    
    startPos = index_pos.get(query, {}).get('start_byte_position', None)
    endPos = index_pos.get(query, {}).get('end_byte_position', None)

    if startPos is not None and endPos is not None:
        query_tf_idf = read_csv_by_byte_range(file, startPos, endPos, query, queries, data, counter)
        q_vector.append(query_tf_idf)
        return
    
    q_vector.append(0)
    return


def read_csv_by_byte_range(csv_file_path, start_byte, end_byte, query, queries, data, counter):
    calc_tf_idf = True
    query_tf_idf = 0

    with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
        header = file.readline().strip()

        file.seek(start_byte)
        current_byte_position = start_byte

        current_byte_position += len(header.encode('utf-8')) + len(file.newlines[-1].encode('utf-8')) if file.newlines else len(header.encode('utf-8'))

        while current_byte_position < end_byte:
            line = file.readline()
            if not line:
                break

            values = line.strip().split(',')

            if len(values) > 1:
                url = values[2]
                
                if calc_tf_idf:
                    calc_tf_idf = False
                    # query_tf_idf = float((queries.count(query) / len(queries)) * (math.log10(float(values[1]) / float(values[3]))))
                    query_tf_idf = float(1 + math.log10(queries.count(query))) * (math.log10(float(values[1]) / float(values[3])))

                data.setdefault(url, {'tf_idf': [], 'weight': 0, 'file': ''})
                data[url]['weight'] += float(values[4])
                data[url]['file'] = values[6]

                for i in range(counter - len(data[url]['tf_idf'])):
                    continue

                data[url]['tf_idf'].append(float(values[5]))

            current_byte_position += len(line.encode('utf-8'))

    return query_tf_idf


def ranking(url_scores):
    return sorted(url_scores.items(), key=lambda item: item[1][0], reverse=True)


def resultsOutput(ranked_urls, top_n=5):
    top_five = []

    print(f"Top {top_n} URLs:")
    for i, url in enumerate(ranked_urls[:top_n], start=1):
        top_five.append((url[0], url[1][1]))
        print(f"{i}. {url}")

    return top_five
