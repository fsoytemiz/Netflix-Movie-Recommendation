import csv
from os import name
from scipy import sparse as sp
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LinearRegression
from scipy.sparse import data


#  Class Movies

class Movies:

    def __init__(self) -> None:
        
        self.sparseData = sp.load_npz('../Data/sample_matrix.npz')
        self.movies, self.active_movies = self._getMovies()
        self.movie_sim = None
        self.model = self.get_trained_model()

    # Trining Model function starts here
    def get_trained_model(self):

        # Function to get Train model
        # return: LinearRegression model

        model = LinearRegression()
        train_data = pd.read_csv('../Data/train_featured.csv')
        X_train, y_train = train_data.iloc[:, 4:].values, train_data.iloc[:, 3].values
        model.fit(X_train, y_train)
        return model

    # Training Model Function ends Here.

    def all(self):
        # returns: All available Movies in our data.
        return self.movies.values.tolist()

    def with_name(self, query):

        # query: A string input by user to search a Movie
        # return: Movies contains that string or Null

        df = self.movies[self.movies.name.str.contains(query, case=False, regex=False)]
        return df.values.tolist()

    def _getMovies(self):

        # return: prepares our data.
        with open('../Data/movie_titles.csv', 'r', encoding='ISO-8859-1') as file:
            lines = csv.reader(file, delimiter=',')
            data = []
            for line in lines:
                row = {}
                row['movie_id'] = line[0]
                row['year'] = line[1]
                row['name'] = ' '.join(line[2:])
                data.append(row)

        ## Movies data frame to store titles.

        movies = pd.DataFrame(data)
        row, column, rating = sp.find(self.sparseData)

        # Sort the data based on Popularity
        uniq_movie = np.unique(column)
        st = []
        for movie in uniq_movie:
            st.append((self.sparseData[:,movie].count_nonzero(), movie))

        st.sort(reverse=True)
        uniq_movie = np.array([item[1] for item in st])
        movies = movies.iloc[uniq_movie - 1]

        del data

        # movies.drop_duplicates('movie_id', inplace=True)

        return movies, uniq_movie
    # _getData ends here


    # Movie to Movie smilarity Function
    def evaluate_movie_sim(self):

        self.movie_sim = cosine_similarity(self.sparseData.T, dense_output=False)
    
    
    # Function to predict Rating for User.

    def predict_rating(self, movieid, userarray, similar_users):

        # returns: numeric rating

        user_global = userarray.sum()/np.count_nonzero(userarray)
        movie_global = self.sparseData[:, movieid].sum()/self.sparseData[:, movieid].count_nonzero()

        similar_movies = self.movie_sim[movieid].toarray().ravel().argsort()[::-1][1:]

        movie_ratings = self.sparseData[similar_users, movieid].toarray().ravel()
        movie_ratings = movie_ratings[movie_ratings != 0][:5]
        movie_ratings = np.hstack((movie_ratings, [0, 0, 0, 0, 0]))
        movie_ratings = movie_ratings[:5]

        user_ratings = userarray[similar_movies]
        user_ratings = user_ratings[user_ratings != 0][:5]
        user_ratings = np.hstack((user_ratings, [0, 0, 0, 0, 0]))
        user_ratings = user_ratings[:5]

        features = np.hstack((movie_ratings, user_ratings, [user_global, movie_global]))
        rating = self.model.predict([features])

        return rating[0]

    
    # Recommendation function is here

    def recommendation(self, user, number):

        # user: An array which contains ratings given by user to some Movies.
        # number: How much results you want
        # return: a List of recommended Movies.

        topk = 10
        movie_box = []
        if self.movie_sim == None:
            self.evaluate_movie_sim()

        similar_users = cosine_similarity([user], self.sparseData).ravel().argsort()[::-1][1:]

        for movie in self.active_movies:
            if user[movie] == 0:
                rating = self.predict_rating(movie, np.array(user), similar_users)
                movie_box.append((rating, movie))

        movie_box.sort(reverse=True)
        array_index = np.array([item[1] for item in movie_box])

        temp = self.movies.copy()
        temp['rating'] = [0]*len(temp)
        for item in movie_box:
            temp.loc[item[1] - 1, 'rating'] = round(item[0], 2)

        return temp.loc[array_index - 1].values.tolist()[:number]

        
    # End of Recommendation FUnction


        