# IR23F-A3-G15
This program takes a very large subset of the UC Irvine's webpages and indexes the information. Using the index
created, the search engine program will return results of the top five most relevant URLs with a brief summary of each
site in less than 300ms.

# Prep
Please use python 3.10.6

Please install the following libraries prior to running program.

python3 -m pip install bs4
python3 -m pip install nltk
python3 -m pip install Flask==3.0.0
python3 -m pip install simhash

After installing the libraries, download the developer.zip folder given by staff and place in the main directory.
(IR23F-A3-G15/developer.zip)

# Start Program
Before running program, please make sure all necessary libraries and all necessary folders are installed. Refer to Prep section for
more information.

To run this start by going into the main directory, (IR23F-A3-G15/) and running "python3 indexer.py" in the terminal. Once completed and the following directories have been generated,
indexer/ indexPos/ and merged/, you can run the search engine by using the command "python3 app.py" which will start
a Flask app. Once the app has started, open the app on a webbrowser and begin searching.

# Team Members
Vedaant Patel (@Vedaantp) - UCINetID: vedaantp - StudentID: 22039484

Jaehoon Song @hoonman - UCINetID: jaehoos1 - StudentID: 16367844

Mohammed Ezzaldiin @mezzaldi - UCINetID: mezzaldi - StudentID: 25665242

Adel Tani @AdelTani - UCINetID: aatani - StudentID: 35898957



