import os
import requests
import operator
import re
from flask import Flask, render_template, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from collections import Counter
from bs4 import BeautifulSoup as bs
import json
import math

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://calvinyu:password@localhost:5432/movie_lists"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)

from models import *
from recommender import *

knn = Recommender()

@app.route('/add-title/', methods=['GET', 'POST'])
def add_title():
	if request.form.getlist('moviepersonal'):
		title = request.form['moviepersonal']
		# title = string_parser(title)
		if Movie.query.filter_by(title=title).first() is None:
			title = string_parser(title)
			url = 'https://www.rottentomatoes.com/m/' + title
		else:
			url = 'https://www.rottentomatoes.com/' + str(Movie.query.filter_by(title=title).first())
		# print(url)

		movie_dict = get_all_scores(url)
		title = string_parser(title, True)
		movie_dict['oscars'] = len(get_all_oscars(title))

		return Response(json.dumps(movie_dict), mimetype='application/json')

@app.route('/submit-titles/', methods=['GET', 'POST'])
def submit_titles():
	movie_dict = request.form.to_dict(flat=False)
	recs = []
	for movie in movie_dict:
		# print(json.loads(movie_dict[movie][0])['title'])
		movie_title = json.loads(movie_dict[movie][0])['title']
		if movie_title[:3] == "The":
			movie_title = movie_title[4:] + str(", the")
		
		recs += knn.predict(movie_title, n_recommendations=5)
	
	recs = [string_parser(str(re.sub("[\(\[].*?[\)\]]", "", str(rec))).strip()) for rec in recs]
	recs = ["the_" + rec[:len(rec) - 4] if rec[-4:] == "_the" else rec for rec in recs]

	print(recs)
	full_movie_dict = {}
	results = []
	for rec in recs:
		try:
			movie_dict = get_all_scores('https://www.rottentomatoes.com/m/' + str(rec))
			movie_dict["oscars"] = len(get_all_oscars(string_parser(rec, caps=True)))
			results.append(movie_dict)
		except:
			pass

	print(results)
	results = sorted(results, key = lambda i: i["cscore"])

	for result in results:
		full_movie_dict[result['title']] = result

	print(full_movie_dict)
	return Response(json.dumps(full_movie_dict), mimetype='application/json')

@app.route('/', methods=['GET', 'POST'])
def index():
	movie_errors = []
	list_errors = []
	results = []
	year_results = []
	genre_results = []
	if request.method == "POST":
		# get url that the person has entered
		try:
			if request.form.getlist('movie'):
				title = request.form['movie']
				title = string_parser(title)
				if str(request.form['format']) == 'movie':
					url = 'https://www.rottentomatoes.com/m/' + title
				else:
					url = 'https://www.rottentomatoes.com/tv/' + title

				movie_dict = get_all_scores(url)

				title = string_parser(title, True)
				movie_dict['oscars'] = len(get_all_oscars(title))

				results.append(movie_dict)

				# print(url)
				# print(movie_dict)

				# try:
				# 	movie_col = Movie(url = url,
				# 		movie_dict = movie_dict)

				# 	db.session.add(movie_col)
				# 	db.session.commit()
				# except Exception as e:
				# 	print("Unable to add item to database")


			elif request.form.getlist('movieyear'):
				year = request.form['movieyear']
				year_results = store_and_show(year=year)

			elif request.form.getlist('moviegenre'):
				genre = str(request.form['moviegenre'])
				genre_results = store_and_show(genre=genre, type_='genre')

		except Exception as e:
			print(e)
			movie_errors.append(
				"Invalid field. Try again."
			)
			return render_template('index.html', movie_errors=movie_errors, list_errors=list_errors)

	return render_template('index.html', movie_errors=movie_errors, list_errors=list_errors,
	 results=results, year_results=year_results, genre_results=genre_results)

@app.route("/movies")
def movies_dic():
	# movies = [{"name": "up"}, {"name": "titanic"}, {"name": "the kings man"}]
	movie_titles = Movie.query.all()
	movie_list = [m.as_dict() for m in movie_titles]
	return jsonify(movie_list)

# HELPERS
def string_parser(string, caps=False):
	if not caps:
		string = string.lower()
	else:
		string = string.title()

	underscore_string = string.replace(" ", "_")
	return re.sub(r'[^\w\s]', '', underscore_string)

# ROTTEN TOMATO SITE
def get_all_scores(url):
	r = requests.get(url)
	# print(r.text)
	soup = bs(r.text, "html.parser")
	movie_dict = {}

	title, t_score, a_score = extract_title_and_scores(soup)
	c_score = calculate_adjusted(soup, title)
	movie_dict["title"] = title
	movie_dict["tscore"] = t_score
	movie_dict["ascore"] = a_score
	movie_dict["cscore"] = c_score

	return movie_dict

def get_all_scores_v2(url, title):
	r = requests.get(url)
	# print(r.text)
	soup = bs(r.text, "html.parser")
	movie_dict["title"] = Movie.query.filter_by(title=title).first().title
	movie_dict["tscore"] = Movie.query.filter_by(title=title).first().t_score
	movie_dict["ascore"] = Movie.query.filter_by(title=title).first().a_score
	movie_dict["cscore"] = calculate_adjusted(soup, title)

	return movie_dict


def extract_title_and_scores(soup):
	info = get_score_info(soup)
	title = info["scoreboard"]["title"]
	a_score = info["modal"]['audienceScoreAll']['score']
	t_score = info["modal"]['tomatometerScoreAll']['score']
	# print(info)
	# main_body = soup.find("div", {"id": "topSection"})
	# thumbnail_info = main_body.find("div", class_="thumbnail-scoreboard-wrap")
	# scores = thumbnail_info.find("score-board", class_="scoreboard")
	# #print(scores['audiencescore'])
	# #print(scores['tomatometerscore'])

	return title, t_score, a_score

def get_score_info(soup):
	all_info = soup.find("script", {"id": "score-details-json"})
	return json.loads(all_info.contents[0])


def calculate_adjusted(soup, title):
	info = get_score_info(soup)
	a_rating = float(info["modal"]['audienceScoreAll']['averageRating'])
	# print(a_rating)
	t_rating = float(info["modal"]['tomatometerScoreAll']['averageRating'])/2
	# print(t_rating)
	a_rating = a_rating/5 * 40
	t_rating = t_rating/5 * 60
	c_rating = round((a_rating + t_rating), 3 - int(math.floor(math.log10(abs((a_rating + t_rating))))) - 1)
	return c_rating + len(get_all_oscars(string_parser(title, caps=True)))


# OSCAR WIKI SITE
def get_all_oscars(movie):
	# print(movie)
	url = 'https://oscars.fandom.com/wiki/' + movie
	r = requests.get(url)
	#print(r.text)
	soup = bs(r.text, "html.parser")	

	noms = soup.find_all("div", class_="mw-parser-output")
	nom_list = []
	if len(noms) > 0:
		noms = noms[0].find_all("ul")
		only_noms = noms[1]
		# print(noms)
		for noms in only_noms.find_all("li"):
			nom_list.append(noms.find("a").contents[0])

	return nom_list

# def get_oscar_info(soup):


def store_and_show(year=None, genre=None, type_='year'):
	full_movie_dict = {}
	results = []

	if type_ == 'year':
		url = 'https://www.rottentomatoes.com/top/bestofrt/?year=' + year
	else:
		url = 'https://www.rottentomatoes.com/top/bestofrt/top_100_' + genre + '_movies/'

	print(url)

	if MovieList.query.filter_by(url=url).first() is None:
		r = requests.get(url)
		#print(r.text)
		soup = bs(r.text, "html.parser")
		# movies = soup.find_all("table", class_="table")

		if type_ == 'year':
			movies = soup.find_all("a", class_="unstyled articleLink", string=lambda text: "(" + year + ")" in text.lower())
		else:
			movies = soup.find_all("a", class_="unstyled articleLink", string=lambda text: "(" in text.lower())


		movie_list = [str(re.sub("[\(\[].*?[\)\]]", "", str(movie.contents[0]))).strip() for movie in movies]
		for movie in movie_list:
			movie = string_parser(movie)
			movie_url = 'https://www.rottentomatoes.com/m/' + movie
			try:
				movie_dict = get_all_scores(movie_url)
				movie = string_parser(movie, True)
				movie_dict['oscars'] = len(get_all_oscars(movie))
				results.append(movie_dict)
				print(movie)
			except:
				pass
			# print(movie_dict)

		results = sorted(results, key = lambda i: i["cscore"], reverse=True)

		for result in results:
			full_movie_dict[result['title']] = result

		try:
			movie_col = MovieList(url = url,
				movie_dict = full_movie_dict)

			db.session.add(movie_col)
			db.session.commit()
		except Exception as e:
			print("Unable to add item to database")
	else:
		full_movie_dict = MovieList.query.filter_by(url=url).first().movie_dict
		for key in full_movie_dict:
			results.append(full_movie_dict[key])

		print(full_movie_dict)

	return results

if __name__ == "__main__":
	# STORE DATA IN DB
	# for i in range(1999, 2015):
	# 	year_results = store_and_show(year=str(i))
	app.run(debug=True)