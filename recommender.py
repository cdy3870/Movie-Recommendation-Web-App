"""
import statements:
"""
# classics
import os
import pandas as pd

# sparse matrix
from scipy.sparse import csr_matrix

# algorithm
from sklearn.neighbors import NearestNeighbors

# string matching
from fuzzywuzzy import fuzz
from Levenshtein import *
from warnings import warn

from fastapi import FastAPI

import pickle

data_path = 'data'
movies_path = 'movies.csv'
ratings_path = 'ratings.csv'
movies = pd.read_csv(
    os.path.join(data_path, movies_path),
    usecols=['movieId', 'title'],
    dtype={'movieId': 'int32', 'title': 'str'})

ratings = pd.read_csv(
    os.path.join(data_path, ratings_path),
    usecols=['userId', 'movieId', 'rating'],
    dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'float32'})

# print(movies.shape)
# print(movies.head())
# print('+-------------------------------+')
# print(ratings.shape)
# print(ratings.head())
# print('+-------------------------------+')
# print(ratings.tail())

# making a pivot of our dataset into features
features = ratings.pivot(
    index='movieId',
    columns='userId',
    values='rating'
).fillna(0)
# Since very large matrices require a lot of memory, we want to scipy sparse and convert our dataframe of our features.
matrix_movie_features = csr_matrix(features.values)
# print('+-------------------------------+')
# print(movie_features.head())
# print('+-------------------------------+')
# now we will isolate films that have been rated 75 times.
# our rating frequency
# number of ratings each movie got.
movie_count = pd.DataFrame(ratings.groupby('movieId').size(), columns=['count'])
# print(movie_count.head())
#
# print('+-------------------------------+')

popularity_level = 75
popular_films = list(set(movie_count.query('count >= @popularity_level').index))
drop_films = ratings[ratings.movieId.isin(popular_films)]
# print('shape of  our  ratings data: ', ratings.shape)
# print('shape of our ratings data after dropping unpopular films: ', drop_films.shape)

# print('+-------------------------------+')
# get the number of ratings given by each user from  our data
user = pd.DataFrame(drop_films.groupby('userId').size(), columns=['count'])
# print(user.head())
#
# print('+-------------------------------+')
# filter data to come to an approximation of user likings.
ratings_level = 75
active_users = list(set(user.query('count >= @ratings_level').index))
drop_users = drop_films[drop_films.userId.isin(active_users)]
# print('shape of original ratings data: ', ratings.shape)
# print('shape of ratings data after dropping both unpopular movies and inactive users: ', drop_users.shape)

# print('+-------------------------------+')

# now we pivot and create our movie-user matrix
user_matrix = drop_users.pivot(index='movieId', columns='userId', values='rating').fillna(0)

# here we are maping  our movie titles
mapper = {
    movie: i for i, movie in
    enumerate(list(movies.set_index('movieId').loc[user_matrix.index].title))
}

movie_user_matrix_sparse = csr_matrix(user_matrix.values)


class Recommender():
	def __init__(self):
		with open('knn_model.pkl', 'rb') as f:
		    model = pickle.load(f)
		self.model = model

	def predict(self, movie, n_recommendations):
		index = self.fuzzy_matcher(mapper, movie, verbose=True)

		if index is None:
			return []

		recs = []
		# print('Popular recommendations: ')
		# print('.....\n')
		distances, indices = self.model.kneighbors(movie_user_matrix_sparse[index], n_neighbors=n_recommendations+1)

		raw_recommends = sorted(
		    list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]
		# reverse mapping and unflattening
		reverse_mapper = {v: k for k, v in mapper.items()}
		# # print recommendations
		# print('Here are more like {}:'.format(movie))
		for i, (index, dist) in enumerate(raw_recommends):
		    # print('{0}: {1}, with distance of {2}'.format(i+1, reverse_mapper[index], dist))
		    # print(reverse_mapper[index])
		    recs.append(reverse_mapper[index])

		return recs

	def fuzzy_matcher(self, mapper, favorite_movie, verbose=True):
	    """

	    We use fuzzy matcher to help get our ratio of movie title names that have been inputed to search through our database.

	    By doing this it will return us the closest match via our fuzzy ratio, which will compare two strings and outputs our ratio.
	    """
	    match_tuple = []
	    # geting our match
	    for title, index in mapper.items():
	        ratio = fuzz.ratio(title.lower(), favorite_movie.lower())
	        if ratio >= 60:
	            match_tuple.append((title, index, ratio))
	            
	    # sorting
	    match_tuple = sorted(match_tuple, key=lambda x: x[2])[::-1]
	    if not match_tuple:
	        print('Movie title mismatch with: ' + str(favorite_movie))
	        return None
	    # if verbose:
	        # print('Top ten similar matches: {0}\n'.format(
	        #     [x[0] for x in match_tuple]))
	        
	    return match_tuple[0][1]