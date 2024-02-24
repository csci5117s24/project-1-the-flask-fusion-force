import db
import json
from os import environ as env
from dotenv import find_dotenv, load_dotenv
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from flask import Flask, request, render_template, redirect, session, url_for, Response, jsonify

from db import successfulLoginAttempt, get_comment, insertNewComment
from spotify import connect_spotify, search_song, refresh_spotify_tokens, spotify_redirect_uri
from auth import require_login
from datetime import datetime, timedelta

def create_app():
  app = Flask(__name__)
  with app.app_context():
      db.setup()
  return app

app = create_app()
@app.route("/")
@app.route('/home', methods=['GET'])
@app.route('/homepage', methods=['GET'])
def homepage():
    return render_template('homepage.html.jinja',user_id = 0,session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4),
   playlists = [{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3']}])

@app.route('/spotify/login', methods=['GET'])
def spotify_login():
  scope = 'user-top-read'
  # Query string is used to retrieve information from a database
  return redirect('https://accounts.spotify.com/authorize?' +
      urlencode({
        "response_type": 'code',
        "client_id": env['SPOTIFY_CLIENT_ID'],
        "scope": scope,
        "redirect_uri": spotify_redirect_uri
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
  session["spotify"] = connect_spotify(session['user_id'], code)
  return render_template('layout.html.jinja')

# Call this route like:.../spotify/search?q=baby%20shark
# The string after "?q=" must be url encoded
# Return a json object where the list of tracks is in the "items" property
# See: https://developer.spotify.com/documentation/web-api/reference/search
@app.route('/spotify/search', methods=['GET'])
def spotify_search():
    if not 'spotify' in session:
       return Response("Need to be logged in to Spotify to use this feature!", status=400, mimetype='text/plain')

    refresh_spotify_tokens(session['user_id'], session['spotify'])

    search_string = request.args.get('q')
    search_res = search_song(session['spotify']['access_token'], search_string)  # flask jsonifies this
    return jsonify(search_res)

@app.route('/search', methods=['POST','GET'])
def search():
  return render_template('search.html.jinja',user_id =1, playlists = [{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3']}])
@app.route('/playlist/<int:p_id>', methods=['POST','GET'])
def playlist(p_id):
  return render_template('playlist.html.jinja', playlist_id=p_id,songs= ["Minnesota March","Minnesota Rouser"],comments= ["Lovely","good vibes"])
@app.route('/settings', methods=['GET'])
# @require_login
def settings():
  return render_template('settings.html.jinja',settings = 
  {"text example":["text"],"show me a cat":["upload"],"Fruits":["dropdown",["oranges","option2"]],"Toggel example":["checkbox"]})

@app.route('/library', methods=['POST','GET'])
# @require_login
def library():
  return render_template('user_library.html.jinja', user_id=session.get('user'))

@app.route('/edit-playlist', methods=['POST','GET'])
# @require_login
def editplaylist():
  return render_template('create_edit_playlist.html.jinja', user_id=session.get('user'),searched_songs= ["Minnesota March","Minnesota Rouser"])

# @app.route('/rate-playlist', methods=['POST'])
def ratePlaylist():
    user_id = request.args.get('user_id')
    playlist_id = request.args.get('playlist_id')
    stars = request.args.get('stars')
    comment = request.args.get('comment')
    if (get_comment(user_id, playlist_id) != []):
        print("User has already left comment for playlist with id: " + str(playlist_id))
    else:
        insertNewComment(user_id, playlist_id, stars, comment)


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
    # Stores user info in the session so we can access the access and refresh tokens
    # Info includes tokens, user_id (.user_info.sub), display name (.userinfo.name)
    token = oauth.auth0.authorize_access_token()
    print(token)
    session["user"] = token
    session["user_id"] = token["userinfo"]["sub"]

    if (successfulLoginAttempt(session["user_id"], token["userinfo"])):
        print("****************")
        print("LOGIN SUCCESSFUL")
        print("****************")

        # Fetch spotify info and store in session
        user = db.checkUser(session["user_id"])[0]  # potential bug: what if no users found? is this possible?
        if (not user.get("spotify_access_token") is None): # spotify acc linked
            app.logger.info(f'found spotify tokens for logged in user {session["user_id"]}, storing in session...')
            spotify_session = {
                "access_token": user.get("spotify_access_token"),
                "refresh_token": user.get("spotify_refresh_token"),
                "expire_time": user.get("spotify_token_expire")
            }
            session['spotify'] = refresh_spotify_tokens(session['user_id'], spotify_session)
        return redirect("/home")
    else:
        print("||||||||||||")
        print("LOGIN FAILED")
        print("||||||||||||")
        return redirect("/login")
    return redirect("/home")

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

