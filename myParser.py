import json
import zipfile
from bs4 import BeautifulSoup
from tokenizer import tokenizing, index_dump, indexes
import multiprocessing
import re
import csv
import zlib
from simhash import Simhash

soup = None
docs = 0
tokens = 0

def checkSimilarity(curr_content, old_content):
    global total_bits

    distance = curr_content.distance(old_content)
    percentage = 1 - distance / total_bits
    if percentage > .9:
        return True

    return False

def compress_string(data):
    compressed_data = zlib.compress(data.encode())
    return compressed_data

def grabContent(content):
    if content:
        # gets the raw html markup of current page using beatiful soup
        currentSoup = BeautifulSoup(content, 'html5lib')
        # removes any other non textual elements
        for unwanted in currentSoup(['script', 'style', 'meta']):
            unwanted.extract()
        # extracts the text
        content = currentSoup.get_text()

        return (' '.join(content.split()))
    
    else:
        return ''

def text_dump(path, data):

    flat_data = []
    for key, value in data.items():
        row = [key, value]
        flat_data.append(row)

    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "Text"])
        writer.writerows(flat_data)

    return

def removeEscapeSequences(text):
    escape_sequence_pattern = r'(\\[ntrufUxX\d]{1,5}|\\u[0-9a-fA-F]{4}|[\']|[\"])'

    return ' '.join((re.sub(escape_sequence_pattern, '', text)).split())


def worker(zip_path, file_list, worker_num, total_docs, total_tokens, total_workers, lock, doc_data):

    text_data = ''
    checkPage = True

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:

        for file in file_list:
            if file.startswith('DEV/') and file.endswith('.json'):
                with zip_ref.open(file) as json_file:
                    json_data = json_file.read().decode('utf-8')

                soup = BeautifulSoup(json_data, 'html.parser')
                data = json.loads(json_data)
                url = data["url"]

                with lock:
                    for doc_d in doc_data:
                        hashed_content = Simhash(grabContent(data.get('content', '')))
                        if not checkSimilarity(hashed_content, doc_d):
                            doc_d.append(hashed_content)

                        else:
                            checkPage = False
                            break

                if checkPage:
                    with lock:
                        total_tokens.append(tokenizing(soup, url, worker_num, file))
                        total_docs.append(1)

                checkPage = True

    path = 'indexes/' + str(worker_num) + '.csv'
    index_dump(path)

    # path = 'textIndex/' + str(worker_num) + '.csv'
    # text_dump(path, text_data)

    global indexes
    indexes = {}
    text_data = ''

    with lock:
        total_workers.append(1)
        print("Workers done: " + str(sum(total_workers)) + '/' + '50')

def parser():
    global soup
    global docs
    global tokens
    zip_path = "developer.zip"
    num_workers = 50

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()

    manager = multiprocessing.Manager()
    total_docs = manager.list()
    total_tokens = manager.list()
    total_workers = manager.list()
    doc_data = manager.list()

    files_per_worker = len(file_list) // num_workers
    file_groups = [file_list[i:i+files_per_worker] for i in range(0, len(file_list), files_per_worker)]

    print("Starting workers")

    processes = []
    for i in range(num_workers):
        process = multiprocessing.Process(target=worker, args=(zip_path, file_groups[i], ('worker' + str(i)), total_docs, total_tokens, total_workers, multiprocessing.Lock(), doc_data))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    print("Workers finished")

    docs = sum(total_docs)
    tokens = sum(total_tokens)

    return docs, tokens