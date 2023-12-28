from flask import Flask, request, render_template
from search import searchQueryUIFlask, openIndexFiles
import timeit

app = Flask(__name__)
index_pos = openIndexFiles()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    start_time = timeit.default_timer()

    query = request.form['query']

    results = searchQueryUIFlask(query, index_pos)

    urls = []
    files = []
    result_array = []

    for res in results:
        urls.append(res[0])
        files.append(res[1])

        url = res[0]
        file = res[1]

        result_array.append({'url': url, 'summary': ''})

    end_time = timeit.default_timer()
    runtime = end_time - start_time
    print(f'Runtime for {query} is {runtime}')
    
    return render_template('search.html', results=result_array, searchQuery=query, runtime=f"{runtime:.4f}")

if __name__ == '__main__':
    # app.run(port=5002, debug=True)
    app.run(port=5002)
