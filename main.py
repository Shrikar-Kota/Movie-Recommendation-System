import numpy as np
import pandas as pd
from flask import Flask, render_template, request, session, redirect, url_for
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import requests
import bcrypt
import pymongo
import os

DB_URL = os.getenv("DB_URL")
db_client = pymongo.MongoClient(DB_URL)
db_name = db_client['Users']
db_collection = db_name['Data']

def create_similarity(index, data):
    # creating a count matrix
    def tokenize(token):
        return token.split("<")
    cv = CountVectorizer(tokenizer = tokenize)
    count_matrix = cv.fit_transform(data['comb'])
    # creating a similarity score matrix
    similarity = cosine_similarity(count_matrix[index], count_matrix)
    return similarity[0]

def rcmd(m):
    m = m.lower()
    try:
        data.head()
        similarity.shape
    except:
        data = pd.read_csv('main_data.csv')
    if m not in data['movie_title'].unique():
        return('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
    else:
        ind = data.loc[data['movie_title']==m].index[0]
        similarity = create_similarity(ind, data)
        lst = list(enumerate(similarity))
        lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
        lst = lst[:11] # excluding first item since it is the requested movie itself
        l = []
        for i in range(len(lst)):
            if len(l) == 10:
                break
            a = lst[i][0]
            if a != ind:
                l.append(data['movie_title'][a])
        return l
    
# converting list of string to list (eg. "["abc","def"]" to ["abc","def"])
def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list

def get_suggestions():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
@app.route("/home")
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    suggestions = get_suggestions()
    user = db_collection.find_one({"email": session['username']})
    if(user):
        if len(user['prev_search']) != 0:
            return render_template('home.html', suggestions=suggestions, not_first_search = True, movie_cards = user['prev_search'])
        else:
            return render_template('home.html', suggestions=suggestions, not_first_search = False)
    else:
        session.pop('username')
        return redirect(url_for('login'))
@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db_collection.find_one({"email":email})
        if user:
            if bcrypt.checkpw(password.encode("utf-8"), user['password'].encode("utf-8")):
                session['username'] = user['email']
                session['SameSite'] = "Strict"
                return {"error": 0}
            else:
                return {"error": 1}
        else:
            return {"error": 1}
    return render_template('login.html')

@app.route("/register", methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = db_collection.find_one({"email":email})
    if not user:
        data = {"email": email, "password": password.decode('utf-8'), "prev_search": []}
        db_collection.insert_one(data)
        return {"success": 1}
    else:
        return {"success": 0}
    
@app.route("/logout", methods=['GET'])
def logout():
    if 'username' not in session:
        return redirect(url_for('home'))
    session.pop('username')
    return {"logout": 1}

@app.route("/similarity",methods=["POST"])
def similarity():
    if 'username' not in session:
        return redirect(url_for('login'))
    movie = request.form['name']
    rc = rcmd(movie)
    if type(rc) == type('string'):
        return rc
    else:
        m_str="<".join(rc)
        return m_str

@app.route("/getgenre",methods=["POST"])
def getgenre():
    if 'username' not in session:
        return redirect(url_for('login'))
    movie = request.form['title'].lower()
    data = pd.read_csv('main_data.csv')
    if movie not in data['movie_title'].unique():
        return {"status": 0}
    else:
        i = data.loc[data['movie_title']==movie].index[0]
        genres = ", ".join(data.iloc[i]['genres'].split(' '))
        return {"status": 1, "genres": genres}

@app.route("/recommend",methods=["POST"])
def recommend():
    if 'username' not in session:
        return redirect(url_for('login'))
    # getting data from AJAX request
    title = request.form['title'].upper()
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_bdays = request.form['cast_bdays']
    cast_bios = request.form['cast_bios']
    cast_places = request.form['cast_places']
    cast_profiles = request.form['cast_profiles']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']

    # call the convert_to_list function for every string that needs to be converted to list
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)
    
    # convert string to list (eg. "[1,2,3]" to [1,2,3])
    cast_ids = cast_ids.split(',')
    cast_ids[0] = cast_ids[0].replace("[","")
    cast_ids[-1] = cast_ids[-1].replace("]","")
    
    # rendering the string to python string
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"','\"')
    
    # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = [(rec_posters[i], rec_movies[i]) for i in range(len(rec_posters))]
    
    casts = {cast_names[i]:[cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}

    cast_details = {cast_names[i]:[cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in range(len(cast_places))}
    
    db_collection.update_one({"email": session["username"]}, {"$set" : {"prev_search" : movie_cards}})

    # passing all the data to the html file
    return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
        release_date=release_date,runtime=runtime,status=status,genres=genres,
        movie_cards=movie_cards,casts=casts,cast_details=cast_details)

if __name__ == '__main__':
    app.run(debug=True)

