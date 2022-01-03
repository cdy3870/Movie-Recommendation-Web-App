from scrape import db
from sqlalchemy.dialects.postgresql import JSON

class MovieList(db.Model):
    __tablename__ = 'movie_lists'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    movie_dict = db.Column(JSON)

    def __init__(self, url, movie_dict):
        self.url = url;
        self.movie_dict = movie_dict

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    title = db.Column(db.String())
    info = db.Column(db.String())
    critics = db.Column(db.String())
    content_rating = db.Column(db.String())
    genre = db.Column(db.String())
    directors = db.Column(db.String())
    authors = db.Column(db.String())
    actors = db.Column(db.String())
    release_date = db.Column(db.Date())
    streaming_date = db.Column(db.Date())
    runtime = db.Column(db.Integer())
    prod_comp = db.Column(db.String())
    tomato_status = db.Column(db.String())
    tomato_score = db.Column(db.Integer())
    tomato_count = db.Column(db.Integer())
    aud_status = db.Column(db.String())
    aud_score = db.Column(db.Integer())
    aud_count = db.Column(db.Integer())
    tomato_top_count = db.Column(db.Integer())
    tomato_fresh = db.Column(db.Integer())
    tomato_rotten  = db.Column(db.Integer())  

    def __init__(self, url):
        self.url = url
        self.t_score = tomato_score
        self.a_score = aud_score
        self.title = title

    def __repr__(self):
        return '{}'.format(self.url)

    def as_dict(self):
        return {'name': self.title}    

# class PersonalMovieList(db.Model):
#     __tablename__ = 'personal_movie_lists'
#     id = db.Column(db.Integer, primary_key=True)
#     movie_dict = db.Column(JSON)

#     def __init__(self, url, movie_dict):
#         self.movie_dict = movie_dict

#     def __repr__(self):
#         return '<id {}>'.format(self.id)