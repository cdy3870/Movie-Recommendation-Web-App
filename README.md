# Movie Recommendation Web App Documentation
### Author: Calvin Yu
### Dates: December 23, 2021
## Description
This document contain a description of the movie recommendation web app done as a side project.

## Main Components
* Frontend: HTML, Javascript, Jquery, and some Bootstrap features
* Backend: Flask, AJAX calls
* Database: Postgres
* Recommender System: KNN model, developed by Jorge Lima (https://github.com/ThisIsJorgeLima/CS-Data-Science-Build-Week-1)

## Python Libraries and Frameworks
* Flask
* Flask-SQLAlchemy
* Beautiful Soup

## Features
* Giving movie recommendations based on a list of movies
	* Enter a movie title, the autocomplete feature grabs data from a database containing movies listed from rotten tomatoes (SQL table is generated from Kaggle dataset: https://www.kaggle.com/stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset)
	* Add title, the AJAX request updates the table, scrapes rotten tomatoes' website for scores and the oscars wiki for number of oscar nominations
	* Submit movie list, movies are grabbed from the table and fed to a recommender system, a modal pops up containing movie recommendations
	sorted based on cal score (see section below)
* Giving a list of movies based on a year or genre
	* Select a year or genre from the dropdowns, (information from the rotten tomatoes' top movies lists are scrapped, sorted by cal score, and stored in postgres database)
	* When submitted, the databased is queried for a list containing the re-sorted rotten tomatoes movie lists

## Cal Score
* A new score is generated based on rotten tomato critic ratings and rotten tomato audience ratings in addition to oscar nominations
	* cal score = (audience rating / 5 * 40) + (critic rating / 5 * 60) + number of oscar nominations, where critics have a higher weighting