import db
import json
from os import environ as env
from dotenv import find_dotenv, load_dotenv
from urllib.parse import quote_plus, urlencode
from flask import Flask, request, render_template, redirect, session, Response, jsonify, url_for
from spotify import get_playlist_info

import auth, db, spotify, api

def create_app():
  app = Flask(__name__)
  app.register_blueprint(auth.app)
  app.register_blueprint(api.app)

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
    #print(db.get_top_playlists()) 
    playlists = []
    print('\nsession\n')
    if (session.get('user_id') != None):
      print("IN IF")
      playlists = db.getUserPlaylists(session['user_id'])
    else:
      print("ELSE")
      playlists = db.getRandomPlaylists(10)
    print('\n\nPLAYLISTS\n')
    print(playlists)
    print('\n')
    return render_template('homepage.html.jinja', user_session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4),
    playlists = playlists)
    # playlists = [{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3']}])

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
  code = request.args.get('code')
  session["spotify"] = spotify.connect_spotify(session['user_id'], code)
  playlist_json = get_playlist_info(session["spotify"].get("access_token"))
  info = []

  # Gets all the playlist information for us in a list of dictionaries where each entry is its own playlist
  for playlist_info in playlist_json.get('items'):
    images = playlist_info.get('images')
    image = images[0].get('url') if images is not None or len(images) > 0 else "NULL"
    info.append({'id':playlist_info.get('id'),'image': image, 'name': playlist_info.get('name'), 'rating': 0})

  # These are the playlists that are already in the database that we use to check for
  db_playlists = db.getPlaylists(session['user_id'])
  db_playlist_ids = [playlist.get('name') for playlist in db_playlists]

  for playlist in info:
    # Makes it so the database won't add a duplicate playlist
    if playlist.get('name') in db_playlist_ids:
        continue
    print(playlist.get('name'))
    playlist_id = db.insert_playlist(session['user_id'], playlist.get('name'), playlist.get('image'))

    songs = spotify.get_songs_from_playlist(session["spotify"].get("access_token"), playlist.get('id'))
    print("SONGS")
    print(songs)

    db.insertSongs(songs)
    db.insertSongsToPlaylist(playlist_id, songs)
  
  # TODO: Can definitely organize it in a better way, I was just strapped for time
  # Gets songs organized by playlist in a nested list of dictionaries -> [[{playlist1_info}], [{playlist2_info}]]
#   for playlist_id in playlist_ids:
#     # playlist_songs.append(spotify.get_songs_from_playlist(session["spotify"].get("access_token"), playlist_id))
#     songs = spotify.get_songs_from_playlist(session["spotify"].get("access_token"), playlist_id)
#     print("SONGS")
#     print(songs)
#     # db.insertSongs(songs)
#     db.insertSongsToPlaylist(playlist_id, songs)

  # TODO: Do I need to insert every song in each playlist to the database or insert it once?
  # TODO: If it's only once then how will we know if that singular song is in the playlist when populating the tracks in the front end
  # TODO: If it's more than once then this will make the website exrtremely slow
  # Brute force method that I think should work but we could definitely improve
#   for playlist in playlist_songs:
  #    for song in playlist:
    # Checks if a song is already in the database or not
  #       if db.get_song_id(song['name'], song['artist'], song['album'], None, song['duration']) == None:
  #          db.insert_song(song['name'], song['artist'], song['album'], None, song['duration'])

  return redirect(url_for("library"))

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
    searchtext = request.form.get("SerchBar")
    print("searchtext= " + str(searchtext))
    if (session.get('user_id') != None):
      searchResults = db.search(session['user_id'], searchtext)
    else:
      searchResults = db.search(None, searchtext)
    print(searchResults)
    return render_template('search.html.jinja',user_id=session.get('user_id'), playlists = [searchResults['name_results'], searchResults['tag_results'], searchResults['saved_results']])
@app.route('/playlist/<int:p_id>', methods=['POST','GET'])
def playlist(p_id):
    songs = db.get_playlist_songs(p_id)
    comments = db.getComments(p_id)
    db_playlist = db.get_playlist_from_playlist_id(p_id)
    playlist = db.get_playlist_from_result(db_playlist)
    user = db.getUserFromPlaylistId(db_playlist[0])
    return render_template('playlist.html.jinja', playlist = playlist, user_image = user[5], playlist_id=p_id,user_session = session.get('user'), user_id=session.get('user_id'), songs = songs,comments = comments)
@app.route('/settings', methods=['GET'])
@auth.require_login
def settings():
    return render_template('settings.html.jinja', user_id=session.get('user_id'),settings = 
  {"Import Spotify playlists":["button",["/spotify/login","get",False]]})

@app.route('/library', methods=['POST','GET'])
@auth.require_login
def library():
    print(session.get('user'))
    #print(db.get_user_playlists(0))
    return render_template('user_library.html.jinja', myPlaylists=[{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3'],'userID':'-1','playlistID':'72',}], savedPlaylists=[{}], randomPlaylists=[{}], user_session=session.get('user'), user_id=session.get('user_id'))

@app.route('/edit-playlist/<int:p_id>', methods=['POST','GET'])
@app.route('/edit-playlist', methods=['POST','GET'])  # Incase user is making a completey new playlist
@auth.require_login
def editplaylist(p_id=None):
    print(p_id)
    if p_id is None:  # New playlist
        return render_template('create_edit_playlist.html.jinja', playlist_id=p_id, user_session=session.get('user'),playlistDetails= [],songs=[],user_id=session.get('user_id'))
    
    playlist_details = [{'playlistID': "someID", 'playlistPicture': "someImg", 'playlistName': "myPlaylist1"}]
    songs = [{'songID': "", 'songName': "mySong1", 'songImage': ""}]
    return render_template('create_edit_playlist.html.jinja', playlist_id=p_id, user_session=session.get('user'),playlistDetails=playlist_details, songs=songs, user_id=session.get('user_id'))

@app.route('/rate-playlist', methods=['POST'])
def ratePlaylist():
    data = request.json
    user_id = data.get('user_id')
    playlist_id = data.get('playlist_id')
    stars = data.get('stars')
    print(user_id)
    print(playlist_id)
    print("stars= " + str(stars))
    comment = data.get('comment')
    db.ratePlaylist(user_id, playlist_id, stars)

@app.route('/add-comment', methods=['POST'])
def addComment():
    data = request.json
    user_id = data.get('user_id')
    playlist_id = data.get('playlist_id')
    comment = data.get('comment')
    print(user_id)
    print(comment)
    db.addComment(user_id, playlist_id, comment)
    # if (db.addComment(user_id, playlist_id, comment) != []):  # TODO fix this. We are adding a rating, not a comment.
    #     print("User has already left comment for playlist with id: " + str(playlist_id))
    # else:
        # db.addComment(user_id, playlist_id, comment)

