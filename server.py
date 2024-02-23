from flask import Flask, request, render_template, redirect, Response, session
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
import requests
import db
from spotify import connect_spotify, redirect_uri, db_get_tokens

def create_app():
  app = Flask(__name__)
  with app.app_context():
      db.setup()
  return app

app = create_app()
app.secret_key = env['FLASK_SECRET']

@app.route('/home', methods=['GET'])
@app.route('/homepage', methods=['GET'])
def homepage():
  return render_template('homepage.html.jinja',user_id = 0, playlists = [{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3']}])

@app.route('/spotify/login', methods=['GET'])
def spotify_login():
  scope = 'user-top-read'
  # Query string is used to retrieve information from a database
  return redirect('https://accounts.spotify.com/authorize?' +
      urlencode({
        "response_type": 'code',
        "client_id": env['SPOTIFY_CLIENT_ID'],
        "scope": scope,
        "redirect_uri": redirect_uri
    },
    quote_via=quote_plus))

@app.route('/spotify/callback', methods=['GET'])
def spotify_callback():
  # FIXME: See if the user has already connected their Spotify account, we'll assume that they have in our situation
  #  if user has already linked their spotify account:
  #    get tokens from database
  #    call function that checks to see if we can use the access token or if we need to use the refresh token
  #    call other functions that will returns the info we need
  # else:
  # if get_db_tokens
  code = request.args.get('code')
  user_id = connect_spotify(code)
  return render_template('layout.html.jinja')

@app.route('/search', methods=['POST','GET'])
def search():
  # FIXME: Figure out how to tell if it's a Spotify song search or if it's searching through the database
  search_url = "https://api.spotify.com/v1/search?q=track:"
  print(request.form)
  return render_template('search.html.jinja',user_id =1, playlists = [{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3']}])
@app.route('/playlist/<int:p_id>', methods=['POST','GET'])
def playlist(p_id):
  return render_template('playlist.html.jinja', playlist_id=p_id,songs= ["Minnesota March","Minnesota Rouser"],comments= ["Lovely","good vibes"])
@app.route('/settings', methods=['GET'])
def settings():
  return render_template('settings.html.jinja',settings = 
  {"text example":["text"],"show me a cat":["upload"],"Fruits":["dropdown",["oranges","option2"]],"Toggel example":["checkbox"]})

@app.route('/library', methods=['POST','GET'])
def library():
  return render_template('user_library.html.jinja', user_id=10)

@app.route('/edit-playlist', methods=['POST','GET'])
def editplaylist():
  return render_template('create_edit_playlist.html.jinja', user_id=1,searched_songs= ["Minnesota March","Minnesota Rouser"])

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
    # FIXME: Store the user_id in the session so we can access the access and refresh tokens
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
    return render_template("layout.html.jinja", user_id=0, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))