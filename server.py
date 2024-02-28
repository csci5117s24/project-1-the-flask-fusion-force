import db
import json
from os import environ as env
from dotenv import find_dotenv, load_dotenv
from urllib.parse import quote_plus, urlencode
from flask import Flask, request, render_template, redirect, session, Response, jsonify, url_for, abort
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
    playlists = db.getRandomPlaylistsOpt(50)
  
    return render_template('homepage.html.jinja', user_session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4),
    playlists = playlists)

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
    print(f"Images: {images}")
    print(f"Images: {len(images)}")
    image = images[0].get('url') if images is not None and len(images) > 0 else "NULL"
    info.append({'id':playlist_info.get('id'),'image': image, 'name': playlist_info.get('name')})

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
    song_ids = [ song.get('id') for song in songs ]
    db.insertSongsToPlaylist(playlist_id, song_ids)

  return redirect(url_for("library"))

# Call this route like:.../spotify/search?q=baby%20shark
# The string after "?q=" must be url encoded
# Return a json object where the list of tracks is in the "items" property
# See: https://developer.spotify.com/documentation/web-api/reference/search
@app.route('/spotify/search', methods=['GET'])
@auth.require_login
def spotify_search():
    print("Spotify searching...")
    if session.get('spotify') is None:
       return Response("Need to be logged in to Spotify to use this feature!", status=400, mimetype='text/plain')

    spotify.refresh_spotify_tokens(session['user_id'], session['spotify'])

    search_string = request.args.get('q')
    num_results = request.args.get('n')
    if (search_string is None): 
       return Response("Need to pass in a query string!", status=400, mimetype='text/plain')
    if (num_results is None): num_results = 20

    search_res = spotify.search_song(session['spotify']['access_token'], search_string)  # flask jsonifies this
    print("Search Results:")
    print(search_res)
    return jsonify(search_res)

@app.route('/search', methods=['POST','GET'])
def search():
    searchtext = request.form.get("SerchBar")
    print("searchtext= " + str(searchtext))
    if (session.get('user_id') != None):
      searchResults = db.search(session['user_id'], searchtext)
    else:
      searchResults = db.search(None, searchtext)
    print(f"Search results:\n{searchResults}")
    nameResults = searchResults['name_results']
    tagResults = searchResults['tag_results']
    savedResults = searchResults['saved_results'] 
    return render_template('search.html.jinja',user_id=session.get('user_id'), nameResults=nameResults, tagResults=tagResults, savedResults=savedResults)

@app.route('/playlist/<int:p_id>', methods=['POST','GET'])
def playlist(p_id):
    # songs = db.get_playlist_songs(p_id)
    # comments = db.getComments(p_id)
    # db_playlist = db.get_playlist_from_playlist_id(p_id)
    # if db_playlist == None:  # playlist w/ playlistID p_id not found
    #     return render_template('403.html.jinja')
    # playlist = db.get_playlist_from_result(db_playlist)
    playlist = db.getPlaylistOpt(p_id)
    songs = db.getPlaylistSongsOpt(p_id)
    comments = db.getComments(p_id)
    user = db.getUserFromPlaylistId(p_id)
    if (session.get('user_id') != None and session['user_id'] == user[0]):
       return redirect(url_for("editPlaylist", p_id=str(p_id)))
    else:
      return render_template('playlist.html.jinja', playlist = playlist, user_image = user[5], playlist_id=p_id,user_session = session.get('user'), user_id=session.get('user_id'), songs = songs,comments = comments)


@app.route('/settings', methods=['GET'])
@auth.require_login
def settings():
    return render_template('settings.html.jinja', user_id=session.get('user_id'),settings = 
  {"Import Spotify playlists":["button",["/spotify/login","get",session.get('spotify')]]})

@app.route('/library', methods=['POST','GET'])
@auth.require_login
def library():
    user_id = session['user']['userinfo']['email']

    # List of dictionaries where each nested list has a playlist's information
    myPlaylists = db.getUserPlaylistsOpt(user_id)
    print(myPlaylists)
    savedPlaylists = db.getSavedPlaylistsOpt(user_id)
    randomPlaylists = db.getRandomPlaylistsOpt(10)
    
    return render_template('user_library.html.jinja', myPlaylists=myPlaylists, savedPlaylists=savedPlaylists, randomPlaylists=randomPlaylists, user_session=session.get('user'), user_id=session.get('user_id'))

@app.route('/create-playlist', methods=['GET'])
@auth.require_login
def createPlaylist():
   return render_template('create_edit_playlist.html.jinja', playlistID=None, user_session=session.get('user'), user_id=session.get('user_id'),
                          playlistDetails={"playlistID": '', "image":'', "name": ''},
                          songs=[])
                        #   songs=[{"songID": "abc123","name": "mySong1","image": ""}])

@app.route('/edit-playlist/<int:p_id>', methods=['GET'])
@auth.require_login
def editPlaylist(p_id):
    # db_playlist = db.get_playlist_from_playlist_id(p_id)
    # print(db_playlist)
    # playlist = db.get_playlist_from_result(db_playlist)
    playlist = db.getPlaylistOpt(p_id)
    songs = db.getPlaylistSongsOpt(p_id)
    print("PLAYLIST SONGS")
    print(playlist)
    print(songs)
    print(f"\n\n\nLENGTH OF SONGS IN PLAYLIST: {len(songs)}\n\n\n")


    if (session.get('user_id') != None and playlist['userID'] == session['user_id']):
    # TODO: uncomment, have playlist as param
    # if userID != session.get('user_id'):
    #    return render_template('403.html.jinja')
    # playlist_details = {'playlistID': "someID", 'playlistPicture': "someImg", 'playlistName': "myPlaylist1"}
    # songs = {"songs": [{"songID": "mySongID", "songName": "mySongName", "songImage": ""}]}
    # if p_id is None:  # New playlist
    #     return render_template('create_edit_playlist.html.jinja', playlist_id=p_id, user_session=session.get('user'),playlistDetails= playlist_details,songs=songs,user_id=session.get('user_id'))
    #   songs = db.get_playlist_songs(p_id)
        print(p_id)
        return render_template('create_edit_playlist.html.jinja', playlistID=p_id, user_session=session.get('user'),
                               playlistDetails=playlist, songs=songs, user_id=session.get('user_id'))
    else:
        return abort(403)

# @app.route('/create-playlist', methods=['POST','GET'])  # Incase user is making a completey new playlist
# @auth.require_login
# def createPlaylist():
#     if (session.get('user_id') != None):
#       playlist = {'playlistID': None, 'userID': None, 'image': None, 'name': None, 'ratingAvg': None, \
#         'numRatings': None, 'tags': None, 'userDisplayName': None}
#       songs = [{'song_id': None, 'name': None, 'picture': None, 'artist': None, 'album': None, 'genre': None, 'duration': None}]
#       return render_template('create_edit_playlist.html.jinja', playlist_id=None, user_session=session.get('user'),playlistDetails=playlist, songs=songs, user_id=session.get('user_id'))

@app.route('/rate-playlist', methods=['POST'])
def ratePlaylist():
    data = request.json
    user_id = data.get('user_id')
    playlist_id = data.get('playlist_id')
    stars = data.get('stars')
    print(user_id)
    print(playlist_id)
    print("stars= " + str(stars))
    db.ratePlaylist(user_id, playlist_id, stars)
    return Response(status=201)

@app.route('/add-comment', methods=['POST'])
def addComment():
    data = request.json
    user_id = data.get('user_id')
    playlist_id = data.get('playlist_id')
    comment = data.get('comment')
    print(user_id)
    print(comment)
    db.addComment(user_id, playlist_id, comment)
    return Response(status=201)
    # if (db.addComment(user_id, playlist_id, comment) != []):  # TODO fix this. We are adding a rating, not a comment.
    #     print("User has already left comment for playlist with id: " + str(playlist_id))
    # else:
        # db.addComment(user_id, playlist_id, comment)

@app.route('/save-playlist', methods=['POST'])
def savePlaylist():
    data = request.json
    user_id = data.get('user_id')
    playlist_id = data.get('playlist_id')
    db.savePlaylist(user_id, playlist_id)
    return redirect(url_for("library"))

@app.route('/test-json')
def send_json():
    data = {"songs": [{"songID": "abc123","songName": "mySong1","songImage": ""}]}
    return json.dumps(data)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html.jinja')