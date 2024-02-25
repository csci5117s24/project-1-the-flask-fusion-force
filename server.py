import db
import json
from os import environ as env
from dotenv import find_dotenv, load_dotenv
from urllib.parse import quote_plus, urlencode
from flask import Flask, request, render_template, redirect, session, Response, jsonify

import auth, db, spotify

def create_app():
  app = Flask(__name__)
  app.register_blueprint(auth.app)

  # load flask secret key
  ENV_FILE = find_dotenv()
  if ENV_FILE:
    load_dotenv(ENV_FILE)
  app.secret_key = env.get("FLASK_SECRET")

  # setup other modules
  with app.app_context():
    db.setup()
    auth.setup()
  return app

app = create_app()
@app.route("/")
@app.route('/home', methods=['GET'])
@app.route('/homepage', methods=['GET'])
def homepage():
    return render_template('homepage.html.jinja',user_id = 0,session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4),
   playlists = [{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3']}])

@app.route('/spotify/login', methods=['GET'])
@auth.require_login
def spotify_login():
  scope = 'user-top-read'
  # Query string is used to retrieve information from a database
  return redirect('https://accounts.spotify.com/authorize?' +
      urlencode({
        "response_type": 'code',
        "client_id": env['SPOTIFY_CLIENT_ID'],
        "scope": scope,
        "redirect_uri": spotify.spotify_redirect_uri
    },
    quote_via=quote_plus))

@app.route('/spotify/callback', methods=['GET'])
@auth.require_login(redirect_to="/spotify/login")
def spotify_callback():
  # FIXME: See if the user has already connected their Spotify account, we'll assume that they have in our situation
  #  if user has already linked their spotify account:
  #    get tokens from database
  #    call function that checks to see if we can use the access token or if we need to use the refresh token
  #    call other functions that will returns the info we need
  # else:
  # if get_db_tokens
  code = request.args.get('code')
  session["spotify"] = spotify.connect_spotify(session['user_id'], code)
  return render_template('layout.html.jinja')

# Call this route like:.../spotify/search?q=baby%20shark
# The string after "?q=" must be url encoded
# Return a json object where the list of tracks is in the "items" property
# See: https://developer.spotify.com/documentation/web-api/reference/search
@app.route('/spotify/search', methods=['GET'])
@auth.require_login
def spotify_search():
    if session.get('spotify') is None:
       return Response("Need to be logged in to Spotify to use this feature!", status=400, mimetype='text/plain')

    spotify.refresh_spotify_tokens(session['user_id'], session['spotify'])

    search_string = request.args.get('q')
    if (search_string is None): 
       return Response("Need to pass in a query string!", status=400, mimetype='text/plain')

    search_res = spotify.search_song(session['spotify']['access_token'], search_string)  # flask jsonifies this
    return jsonify(search_res)

@app.route('/search', methods=['POST','GET'])
def search():
  return render_template('search.html.jinja',user_id =1, playlists = [{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3']}])
@app.route('/playlist/<int:p_id>', methods=['POST','GET'])
def playlist(p_id):
  return render_template('playlist.html.jinja', playlist_id=p_id,songs= ["Minnesota March","Minnesota Rouser"],comments= ["Lovely","good vibes"])
@app.route('/settings', methods=['GET'])
@auth.require_login
def settings():
  return render_template('settings.html.jinja',settings = 
  {"text example":["text"],"show me a cat":["upload"],"Fruits":["dropdown",["oranges","option2"]],"Toggel example":["checkbox"]})

@app.route('/library', methods=['POST','GET'])
@auth.require_login
def library():
  return render_template('user_library.html.jinja', user_id=session.get('user'))

@app.route('/edit-playlist', methods=['POST','GET'])
@auth.require_login
def editplaylist():
  return render_template('create_edit_playlist.html.jinja', user_id=session.get('user'),searched_songs= ["Minnesota March","Minnesota Rouser"])

# @app.route('/rate-playlist', methods=['POST'])
def ratePlaylist():
    user_id = request.args.get('user_id')
    playlist_id = request.args.get('playlist_id')
    stars = request.args.get('stars')
    comment = request.args.get('comment')
    if (db.get_comment(user_id, playlist_id) != []):
        print("User has already left comment for playlist with id: " + str(playlist_id))
    else:
        db.insertNewComment(user_id, playlist_id, stars, comment)