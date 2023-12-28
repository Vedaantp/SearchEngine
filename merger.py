import os
import math
import csv
import heapq
from tempfile import TemporaryDirectory

def my_sort(input_file, output_file, sort_column):
    def sort_chunk(chunk):
        
        header, *data = chunk
        data.sort(key=lambda row: row[sort_column])
        return [header, *data]

    chunk_size = 10000
    chunks = []

    with open(input_file, 'r', newline='') as infile:
        reader = csv.reader(infile)
        header = next(reader)

        chunk = [header]
        for row in reader:
            chunk.append(row)
            if len(chunk) == chunk_size:
                chunks.append(chunk)
                chunk = [header]

        if chunk:
            chunks.append(chunk)

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)

        writer.writerow(header)

        for row in heapq.merge(*(sort_chunk(chunk) for chunk in chunks), key=lambda row: row[sort_column]):
            writer.writerow(row)

def dump_csv(data, path):
    flat_data = []
    for key, values in data.items():
        doc_freq = values["doc_freq"]
        for url, doc_info in values["docs"].items():
            row = [key, doc_freq, url, doc_info["frequency"], doc_info["weight"], doc_info["tf_idf"], doc_info['file']]
            flat_data.append(row)

    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Doc_Freq", "URL", "Frequency", "Weight", "TF_IDF", 'File'])
        writer.writerows(flat_data)

    return

def convert_csv_to_dict(path):
    data_list = []

    with open(path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            data_list.append(row)

    csv_dict = {}

    for row in data_list:
        try:
            name = row['Name']


            if name not in csv_dict:
                csv_dict[name] = {
                    'doc_freq': int(row['Doc_Freq']),
                    'docs': {},
                }

            url = row['URL']
            csv_dict[name]['docs'][url] = {
                'frequency': int(row['Frequency']),
                'weight': int(row['Weight']),
                'tf_idf': float(row['TF_IDF']),
                'file': row['File']
            }

        except:
            continue

    return csv_dict

def merge_csv(files, total_docs):

    merged = {}
    key = ''
    value = 0
    counter = 0

    print("Aggregating the doc frequencies")
    for file in files:
        counter += 1

        path = 'indexes/' + file
        with open(path, 'r', newline='', encoding='utf-8') as file:
            header = file.readline().strip()

            while True:

                line = file.readline()
                if not line:
                    break

                values = line.strip().split(',')
                row_dict = dict(zip(header.split(','), values))

                if key == '':
                    key = row_dict['Name']
                    value = int(row_dict['Doc_Freq'])

                elif row_dict['Name'] != key:
                    if merged.get(key, None) is None:
                        merged[key] = value
                    else:
                        merged[key] += value

                    key = row_dict['Name']
                    value = int(row_dict['Doc_Freq'])

        print(f"{counter}/{len(files)} done")


    counter = 0 
    print("Merging files")
    with open('merged/merged.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Doc_Freq", "URL", "Frequency", "Weight", "TF_IDF", 'File'])

        for file in files:
            counter += 1
            path = 'indexes/' + file
            with open(path, 'r', newline='', encoding='utf-8') as f2:
                header = f2.readline().strip()

                while True:

                    line = f2.readline()
                    if not line:
                        break

                    values = line.strip().split(',')
                    row = [values[0], merged.get(values[0], 0), values[2], values[3], values[4], (float(values[5]) * math.log10(total_docs / merged[values[0]])), values[6]]
                    writer.writerow(row)

            print(f"{counter}/{len(files)} done")
    return

def merge_start(total_docs):
    print("Starting merge")

    files = os.listdir('indexes/')

    merge_csv(files, total_docs)
    my_sort('merged/merged.csv', 'merged/sorted.csv', 0)

    print("Merging Done")

    return