from flask.json import jsonify
from recommendation import Movies
from flask import Flask, render_template, url_for, request

app = Flask(__name__)
movies = Movies()                           # movies object
user, movie = movies.sparseData.shape       # GEt the shape of sparseData
NO_OF_MOVIE = movie                         # number of movies in our data
# user = [0]*NO_OF_MOVIE                      # Array to be used for recommendations.

# This is testing

@app.route('/<string:name>')
def hello(name):
    return f"Hello {name}"


# Route for recommendations
@app.route('/recommendation')
def recommendation():
    result = movies.recommendation(user, 10)
    return render_template('recommendation.html', results=result)

# This is Home
@app.route('/')
def Home():
    global user
    user = [0]*NO_OF_MOVIE
    results = movies.all()
    # print(results)
    return render_template('index.html', results = results)

 
#  This is About page.
@app.route('/About')
def About():
    return render_template('about.html')   

#  This is for searching something.
@app.route('/search', methods=['POST'])
def search():
    keyword = request.form.get('query')
    results = []
    if keyword:
        results = movies.with_name(keyword)
    return render_template('results.html', results=results)


# This handles ajax request to set Rating  for a Given Movie.

@app.route('/setRating', methods=['POST'])
def setRating():
    rating = request.form.get('rating')
    id = request.form.get('id')
    user[int(id)] = int(rating)
    return jsonify(status="success")


# This is Main Function
if __name__ == '__main__':
    app.run(debug=True)