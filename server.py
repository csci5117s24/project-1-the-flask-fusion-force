from flask import Flask, request, render_template, redirect, Response
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
import requests
import base64

app = Flask(__name__)
redirect_uri = "http://127.0.0.1:5000/callback"


@app.route('/', methods=['GET'])
def layout():
  return render_template('layout.html.jinja',user_id = 0)

@app.route('/home', methods=['GET'])
@app.route('/homepage', methods=['GET'])
def homepage():
  return render_template('homepage.html.jinja',user_id = 0, playlists = [{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3']}])

@app.route('/login', methods=['GET'])
def login():
  scope = 'user-top-read'
    # Query string is used to retrieve information from a database
  json = {
        "response_type": 'code',
        "client_id": env['SPOTIFY_CLIENT_ID'],
        "scope": scope,
        "redirect_uri": "http://127.0.0.1:5000/callback"
    }
  return redirect('https://accounts.spotify.com/authorize?' +
      urlencode({
        "response_type": 'code',
        "client_id": env['SPOTIFY_CLIENT_ID'],
        "scope": scope,
        "redirect_uri": redirect_uri
    },
    quote_via=quote_plus))

@app.route('/callback', methods=['GET'])
def callback():
  code = request.args.get('code')

  credentials_str = f"{env['SPOTIFY_CLIENT_ID']}:{env['SPOTIFY_CLIENT_SECRET']}"
  credentials_bytes = credentials_str.encode('ascii')

  base64_bytes = base64.b64encode(credentials_bytes)
  base64_str = base64_bytes.decode("ascii")

  auth_options = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': 'Basic ' + base64_str
        }
  
  data = {
    "code": code,
    "redirect_uri": redirect_uri,
    "grant_type": 'authorization_code'
  }
  
  # FIXME: Why do I have to login everytime?
  response = requests.post(url='https://accounts.spotify.com/api/token', data=data, headers=auth_options)
  response_json = response.json()
  access_token = response_json.get('access_token')
  print("Accessing " + str(response_json.get('access_token')))

  playlist_url = "https://api.spotify.com/v1/me/playlists"
  playlist_headers = {'Authorization': 'Bearer ' + access_token}
  playlist_rsp = requests.get(url=playlist_url, headers=playlist_headers)
  playlist_json = playlist_rsp.json()
  print(playlist_json)
  
  return render_template('layout.html')

'''
@app.route('/search', methods=['POST'])
def search():
  return render_template('search.html')

@app.route('/playlist/<int:p_id>', methods=['POST'])
def playlist(p_id):
  return render_template('playlist.html', playlist_id=p_id)

@app.route('/login', methods=['GET'])
def login():
  return render_template('login.html')

@app.route('/settings', methods=['GET'])
def settings():
  return render_template('settings.html')

@app.route('/library/<int:u_id>', methods=['POST'])
def library(u_id):
  return render_template('library.html', user_id=u_id)
'''
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import redirect, session, url_for

# app = Flask(__name__)
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
app.secret_key = env.get("FLASK_SECRET")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/")
def home():
    return render_template("home.html", user_id=0, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

from contextlib import contextmanager
import logging

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None

def setup():
    global pool
    DATABASE_URL = env['DATABASE_URL']
    current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode='require')


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
      cursor = connection.cursor(cursor_factory=DictCursor)
      try:
          yield cursor
          if commit:
              connection.commit()
      finally:
          cursor.close()

def get_playlist(playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_playlists WHERE playlist_id=%s;", playlist_id)
    return cursor.fetchall()

def get_playlist_songs_ids(playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT song_id FROM mixtape_fm_playlist_songs WHERE playlist_id=%s;", playlist_id)
    return cursor.fetchall()

def get_songs_from_song_id(song_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_songs WHERE song_id=%s;", song_id)
    return cursor.fetchall()

def get_playlist_songs(playlist_id):
  playlist_songs_ids = get_playlist_songs_ids(playlist_id)
  playlist_songs = []
  for song_id in playlist_songs_ids:
    playlist_songs.append(get_songs_from_song_id(song_id))
  return playlist_songs

def get_user_playlists(user_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_playlists WHERE user_id=%s;", user_id)
    return cursor.fetchall()

def get_playlist_id(user_id, playlist_name):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT playlist_id FROM mixtape_fm_playlists WHERE user_id=%s, playlist_name=%s;", (user_id, playlist_name))
    return cursor.fetchall()

def get_playlist_song_id(playlist_id, song_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT playlist_song_id FROM mixtape_fm_playlist_songs WHERE playlist_id=%s, song_id=%s;", (playlist_id, song_id))
    return cursor.fetchall()

def get_song_id(name, artist, album, genre, duration):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT song_id FROM mixtape_fm_songs WHERE name=%s, artist=%s, album=%s, genre=%s, duration=%s;", \
    (name, artist, album, genre, duration))
    return cursor.fetchall()

def get_comment_id(commenter_id, playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_comments WHERE comment_user_id=%s, playlist_id=%s;", (commenter_id, playlist_id))
    return cursor.fetchall()

def insert_playlist(user_id, playlist_name):
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_playlists (user_id, playlist_name, creation_date) VALUES (%s, %s, CURRENT_TIMESTAMP);", \
    (user_id, playlist_name))
    return get_playlist_id(user_id, playlist_name)

def insert_song_into_playlist(playlist_id, song_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_playlist_songs (playlist_id, song_id) VALUES (%s, %s);", (playlist_id, song_id))
    return get_playlist_song_id(playlist_id, song_id)

def insert_song(name, artist, album, genre, duration):
  if (get_song_id(name, artist, album, genre, duration) == None):
    with get_db_cursor(True) as cursor:
      cursor.execute("INSERT INTO mixtape_fm_songs (name, artist, album, genre, duration) VALUES (%s, %s, %s, %s, %s);", \
      (name, artist, album, genre, duration))
      return get_song_id(name, artist, album, genre, duration)

def insert_new_user(user_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_users (user_id, spotify_linked) VALUES (%s, %s);", (user_id, 'FALSE'))
    return

def insert_new_comment(commenter_id, playlist_id, stars, content):
  if (stars < 1 or stars > 5):
    print("Invalid number of stars in review")
    return None
  if (get_comment_id(commenter_id, playlist_id) != None):
    print("User has already left a review of this playlist")
    return None
  with get_db_cursor(True) as cursor:
    if (content == None or content == ''):
      cursor.execute("INSERT INTO mixtape_fm_comments (comment_user_id, playlist_id, stars, timestamp) VALUES (%s, %s, %s, CURRENT_TIMESTAMP);", \
      (commenter_id, playlist_id, stars))
    else:
      cursor.execute("INSERT INTO mixtape_fm_comments (comment_user_id, playlist_id, stars, content, timestamp) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP);", \
      (commenter_id, playlist_id, stars, content))
    return get_comment_id(commenter_id, playlist_id)
