from myParser import parser
from merger import merge_start
from indexPos import calc_index
import os
import datetime

# machine 12 vedaantp

if not os.path.exists('indexes/'):
    os.makedirs('indexes/')

if not os.path.exists('merged/'):
    os.makedirs('merged/')

if not os.path.exists('indexPos/'):
    os.makedirs('indexPos/')


start = str(datetime.datetime.now())

total_docs, total_tokens = parser()

merge_start(total_docs)
# merge_text()

calc_index()
# calc_text()

end = str(datetime.datetime.now())

with open('report.txt', 'a') as f:
    f.write("################ Report ################\n")
    f.write("Started Time: " + start + '\n')
    f.write("Ended Time: " + end + '\n')
    f.write("Total documents: " + str(total_docs) + '\n')
    f.write("Total Tokens: " + str(total_tokens) + '\n')
    
    total_size = 0

    if os.path.exists('merged/'):
        files = os.listdir('merged/')

        for file in files:
            f.write('Size of ' + str(file) + ': ' + str(os.path.getsize('merged/' + str(file)) // 1024) + ' KB\n')
            total_size += os.path.getsize('merged/' + str(file)) // 1024

    if os.path.exists('indexPos/'):
        files = os.listdir('indexPos/')

        for file in files:
            f.write('Size of ' + str(file) + ': ' + str(os.path.getsize('indexPos/' + str(file)) // 1024) + ' KB\n')
            total_size += os.path.getsize('indexPos/' + str(file)) // 1024

    f.write('Size of total index: ' + str(total_size) + ' KB\n')

    f.write("########################################\n")