from contextlib import contextmanager
import os
import random
from flask import current_app, jsonify
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor
import math
pool = None

def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
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

### *************************************************************************************
### *************************************************************************************
### ******************************GETTER / SELECT FUNCTIONS******************************
### *************************************************************************************
### *************************************************************************************
def get_playlist(playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_playlists WHERE playlist_id=%s;", (playlist_id,))
    return cursor.fetchall()

def get_playlist_songs_ids(playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT song_id FROM mixtape_fm_playlist_songs WHERE playlist_id=%s;", (playlist_id,))
    return cursor.fetchall()

def get_song_from_song_id(song_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_songs WHERE song_id=%s;", (song_id,))
    return cursor.fetchone()

def get_playlist_songs(playlist_id):
  playlist_songs_ids = get_playlist_songs_ids(playlist_id)
  playlist_songs = []
  for song_id_arr in playlist_songs_ids:
    song_id = song_id_arr[0]
    song_result = get_song_from_song_id(song_id)
    # songs: [song_id:””, name:””, picture:”img”, artist:’’”, album:””, genre:””|null, duration:””|null]
    duration = None
    if (song_result[5]):
      duration = str(math.floor(int(song_result[5]) / 60000)) + ':' + str(int(song_result[5]) % 60000)
      # print("duration= " + duration)
    song = {'song_id': song_result[0], 'name': song_result[1], 'picture': song_result[6], 'artist': song_result[2], 'album': song_result[3], 'genre': song_result[4], 'duration': duration}
    playlist_songs.append(song)
  return playlist_songs

def get_user_playlists(user_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_playlists WHERE user_id=%s;", (user_id,))
    return cursor.fetchall()

def get_playlist_id(user_id, playlist_name):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT playlist_id FROM mixtape_fm_playlists WHERE user_id=%s AND playlist_name=%s;", (user_id, playlist_name))
    return cursor.fetchone()

def getPlaylistId(user_id, playlist_name):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT playlist_id FROM mixtape_fm_playlists WHERE user_id=%s AND playlist_name=%s;", (user_id, playlist_name))
    return cursor.fetchone()

def get_playlist_song_id(playlist_id, song_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT playlist_song_id FROM mixtape_fm_playlist_songs WHERE playlist_id=%s AND song_id=%s;", (playlist_id, song_id))
    return cursor.fetchone()

def getPlaylistSongId(playlist_id, song_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT playlist_song_id FROM mixtape_fm_playlist_songs WHERE playlist_id=%s AND song_id=%s;", (playlist_id, song_id))
    return cursor.fetchone()

def get_song_id(name, artist, album, genre, duration, image):
  with get_db_cursor(True) as cursor:
    if (genre == None):
      cursor.execute("SELECT song_id FROM mixtape_fm_songs WHERE name=%s AND artist=%s AND album=%s AND duration=%s;", \
      (name, artist, album, duration))
    else:
      cursor.execute("SELECT song_id FROM mixtape_fm_songs WHERE name=%s AND artist=%s AND album=%s AND genre=%s AND duration=%s;", \
      (name, artist, album, genre, duration))
    return cursor.fetchone()

def get_comment(commenter_id, playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_comments WHERE comment_user_id=%s AND playlist_id=%s;", (commenter_id, playlist_id))
    return cursor.fetchall()

def get_tag_id(tag_name):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_tags WHERE tag_name=%s;", (tag_name,))
    return cursor.fetchone()

def checkUser(user_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_users WHERE user_id=%s;", (str(user_id), ))
    return cursor.fetchall()

def successfulLoginAttempt(user_id, user_display_name, image):
  print("user_id= " + str(user_id))
  if (user_id == None):
    return False
  checkVal = checkUser(user_id)
  if (checkVal == []):
    with get_db_cursor(True) as cursor:
      cursor.execute("INSERT INTO mixtape_fm_users (user_id, user_display_name, image) VALUES (%s, %s, %s);", (str(user_id), str(user_display_name), str(image)))
      return True
  else:
    return True

def playlist_search(variation, search_word):
  with get_db_cursor(True) as cursor:
    search_symbol = ''
    if (variation == 1):
      search_symbol = '%' + search_word + '%'
    elif (variation == 2):
      search_symbol = '% ' + search_word + '%'
    elif (variation == 3):
      search_symbol = '%' + search_word + ' %'
    elif (variation == 4):
      search_symbol = '% ' + search_word + ' %'
    elif (variation == 5):
      search_symbol = '% ' + search_word + '.%'
    elif (variation == 6):
      search_symbol = '%' + search_word + ',%'
    else:
      print("variation value %d invalid", (variation))
      return None
    cursor.execute("SELECT * FROM mixtape_fm_playlists WHERE playlist_name LIKE %s;", (search_symbol, ))
    return cursor.fetchall()

def tag_id_search(variation, search_word):
  with get_db_cursor(True) as cursor:
    search_symbol = ''
    if (variation == 1):
      search_symbol = '%' + search_word + '%'
    elif (variation == 2):
      search_symbol = '% ' + search_word + '%'
    elif (variation == 3):
      search_symbol = '%' + search_word + ' %'
    elif (variation == 4):
      search_symbol = '% ' + search_word + ' %'
    elif (variation == 5):
      search_symbol = '% ' + search_word + '.%'
    elif (variation == 6):
      search_symbol = '%' + search_word + ',%'
    else:
      print("variation value %d invalid", (variation))
      return None
    cursor.execute("SELECT tag_id FROM mixtape_fm_tags WHERE tag_name LIKE %s;", (search_symbol, ))
    return cursor.fetchall()

def get_playlist_id_from_tag_id(tag_id):
  if (tag_id == None):
    return None
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT playlist_id FROM mixtape_fm_playlist_tags WHERE tag_id = %s;", (tag_id, ))
    return cursor.fetchone()

def get_playlist_from_playlist_id(playlist_id):
  if (playlist_id == None):
    return None
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_playlists WHERE playlist_id = %s;", (playlist_id, ))
    return cursor.fetchone()

def get_playlists_from_tag_id_results(tag_id_results):
  playlists = []
  if (tag_id_results):
    for tag_id_result in tag_id_results:
      if (tag_id_result):
        playlist_id = get_playlist_id_from_tag_id(tag_id_result[0])
        if (playlist_id):
          playlists.append(playlist_id[0])
  return get_playlists_from_results(playlists)

# TODO
# def get_if_saved(playlist_result):
#   with get_db_cursor(True) as cursor:
#     cursor.execute("SELECT * FROM mixtape_fm_playlists WHERE playlist_id")

# TODO
# def get_playlists_from_saved_results(playlist_results):
#   saved_results = []
#   if (playlist_results):
#     for playlist_result in playlist_results:
#       saved_result = get_if_saved(playlist_result)
#       if (saved_result != None and saved_result != []):
#         saved_results.append(saved_result)
#   return get_playlists_from_results(saved_results)


# TODO: Create search keyword matching, using sql operators 'like' and 'ilike'
## Make a function compiling results from searching for songs in db and playlists, tags preferable
def search(user_id, search_word):
  ret_dict = {}
  ret_dict['name_results'] = []
  ret_dict['tag_results'] = []
  ret_dict['saved_results'] = []
  print(search_word)
  if (search_word == None or search_word == ''):
    return ret_dict
  playlist_results = []
  tag_id_results = []
  for variation in range(1, 7):
    playlist_results = playlist_results + playlist_search(variation, search_word)
    tag_id_results = tag_id_results + tag_id_search(variation, search_word)
  name_results = get_playlists_from_results(playlist_results)
  tag_results = get_playlists_from_tag_id_results(tag_id_results)
  if (user_id != None):
    saved_results = get_saved_playlists(user_id)
  else:
    saved_results = []
  # saved_results = get_playlists_from_saved_results(playlist_results)
  ret_dict['name_results'] = name_results
  ret_dict['tag_results'] = tag_results
  ret_dict['saved_results'] = saved_results
  return ret_dict


# def search(search_word):
#   ret_dict = {}
#   if (search_word == None or search_word == ''):
#     return ret_dict
#   playlist_results = []
#   tag_results = []
#   tag_ids = []
#   playlist_ids = []
#   for variation in range(1, 7):
#     # playlist_results = playlist_results + playlist_search(variation, search_word)
#     p_s_results = playlist_search(variation, search_word)
#     for result in p_s_results:
#       tags = []
#       db_tag_ids = get_tag_ids_from_playlist_id(result[0])
#       for db_tag_id in db_tag_ids:
#         db_tag = get_tag_from_id(db_tag_id[0])
#         tags.append(db_tag[0])
#       avg_rating = getRatingAvg(result[0])
#       playlist_results.append({'image': result[4],'name': result[2],'rating': avg_rating[0],'tags': tags})
#     tag_ids = tag_ids + tag_id_search(variation, search_word) # Need to get tag_ids
#   for tag_id in tag_ids:
#     p_t_id = get_playlist_id_from_tag_id(tag_id)
#     playlist_ids.append(p_t_id[0]) # Need to get playlist_ids corresponding to tag_ids
#   for playlist_id in playlist_ids:
#     db_playlist = get_playlist_from_playlist_id(playlist_id)
#     tag_results.append(db_playlist[0])
#     # tag_results = tag_results +  get_playlist_from_playlist_id(playlist_id) # Finally, need to get playlists based on initial tag search word
#   ret_dict["playlist_results"] = playlist_results
#   ret_dict["tag_results"] = tag_results
#   return ret_dict

## HELPER FUNCTION TO GET TAGS FOR PLAYLSITS
def get_tag_ids_from_playlist_id(playlist_id):
  if (playlist_id == None):
    return []
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT tag_id FROM mixtape_fm_playlist_tags WHERE playlist_id = %s;", (playlist_id, ))
    return cursor.fetchall()

## HELPER FUNCTION TO GET TAGS FOR PLAYLISTS
def get_tag_from_id(tag_id):
  if (tag_id == None):
    return []
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT tag_name FROM mixtape_fm_tags WHERE tag_id = %s;", (tag_id, ))
    return cursor.fetchone()

## HELPER FUNCTION TO GET PLAYLISTS
def getRatingAvg(playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT AVG(stars) FROM mixtape_fm_ratings WHERE playlist_id = %s;", (playlist_id, ))
    return cursor.fetchone()

# HELPER FUNCTION TO GET PLAYLISTS
def getUserIdFromPlaylistId(playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT user_id FROM mixtape_fm_playlists WHERE playlist_id = %s;", (playlist_id, ))
    return cursor.fetchone()

## HELPER FUNCTION TO GET PLAYLISTS
def getUserFromUserId(user_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_users WHERE user_id = %s;", (user_id, ))
    return cursor.fetchone()

## returns user info 
def getUserFromPlaylistId(playlist_id):
  user_id = getUserIdFromPlaylistId(playlist_id)
  user = []
  if (user_id):
    user = getUserFromUserId(user_id[0])
  return user

def getRatingsNoUser(playlist_id):
  ratings = []
  if (playlist_id == None):
    return ratings
    # return jsonify(ratings)
  db_ratings = get_ratings_no_user(playlist_id)
  ratings = get_ratings_from_db_ratings(db_ratings)
  return ratings
  # return jsonify(ratings) 

def get_playlist_from_result(playlist_result):
  playlist = {'playlistID': None, 'image': None, 'name': None, 'ratingAvg': None, \
    'numRatings': None, 'tags': None, 'userDisplayName': None}
  if (playlist_result == [] or playlist_result == None):
    return playlist
  else:
    ratings = getRatingsNoUser(playlist_result[0])
    tag_ids = get_tag_ids_from_playlist_id(playlist_result[0])
    user = getUserFromPlaylistId(playlist_result[0])
    tags = []
    for tag_id in tag_ids:
      db_tag = get_tag_from_id(tag_id[0])
      tags.append(db_tag[0])
    db_ratingAvg = getRatingAvg(playlist_result[0])
    ratingAvg = 0
    if (db_ratingAvg[0]):
      ratingAvg = str(round(float(db_ratingAvg[0]), 2))
    playlist = {'playlistID': playlist_result[0], 'image': playlist_result[4], 'name': playlist_result[2], 'ratingAvg': ratingAvg, \
    'numRatings': len(ratings), 'tags': tags, 'userDisplayName': user[3]}
    return playlist

## HELPER FUNCTION TO GET PLAYLISTS
def get_playlists_from_results(playlist_results):
  playlists = []
  for playlist in playlist_results:
    # ratings = get_comments(playlist[0]) TODO
    ratings = getRatingsNoUser(playlist[0])
    tag_ids = get_tag_ids_from_playlist_id(playlist[0])
    user = getUserFromPlaylistId(playlist[0])
    tags = []
    for tag_id in tag_ids:
      db_tag = get_tag_from_id(tag_id[0])
      tags.append(db_tag[0])
      # tags = tags + get_tag_from_id(tag_id[0])
    # Get average from ratings
    db_ratingAvg = getRatingAvg(playlist[0])
    ratingAvg = 0
    if (db_ratingAvg[0]):
      ratingAvg = str(round(float(db_ratingAvg[0]), 2))
    playlists.append({'playlistID': playlist[0], 'image': playlist[4], 'name': playlist[2], 'ratingAvg': ratingAvg, \
    'numRatings': len(ratings), 'tags': tags, 'userDisplayName': user[3]})
  return playlists

# Takes user_id, returns array with {name, image, ratings, tags[], playlist_id}
def getPlaylists(user_id):
  if (user_id == None):
    return []
  playlist_results = get_user_playlists(user_id)
  playlists = get_playlists_from_results(playlist_results)
  return playlists
  # return jsonify(playlists)

def get_top_playlist_ids():
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT playlist_id FROM mixtape_fm_ratings ORDER BY stars DESC LIMIT 10;")
    return cursor.fetchall()

def get_top_playlists():
  playlist_ids = get_top_playlist_ids()
  playlist_results = []
  for playlist_id in playlist_ids:
    playlist_result = get_playlist_from_playlist_id(playlist_id)
    playlist_results.append(playlist_result[0])
    # playlist_results.append(get_playlist_from_playlist_id(playlist_id))
  return playlist_results

## Get 10 top rated playlists across the site
def getTopRatedPlaylists():
  playlist_results = get_top_playlists()
  playlists = get_playlists_from_results(playlist_results)
  return playlists
  # return jsonify(playlists)

def get_random_playlists(n):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_playlists ORDER BY random() LIMIT %s;", (n, ))
    return cursor.fetchall()

## Gets n random playlists, returns array with {name, image, ratings, tags[], playlist_id}
def getRandomPlaylists(n):
  if (n == None or n <= 0):
    return []
  # playlist_results = get_user_playlists(user_id)
  playlist_results = get_random_playlists(n)
  playlists = get_playlists_from_results(playlist_results)
  return playlists
  # playlists = get_playlists_from_results(playlist_results)
  # if (len(playlists) < n):
  #   return playlists
  #   # return jsonify(playlists)
  # else:
  #   random_playlists = random.sample(playlists, n)
  #   return random_playlists
  #   # return jsonify(random_playlists)

def isPlaylistRecent(user_id, playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_user_recent_playlists WHERE user_id = %s AND playlist_id = %s;", (user_id, playlist_id))
    return cursor.fetchall()

def updatePlaylistRecent(user_id, playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("UPDATE mixtape_fm_user_recent_playlists SET timestamp = CURRENT_TIMESTAMP WHERE user_id = %s AND playlist_id = %s;", \
    (user_id, playlist_id))
    return

def playlistLeastRecent(user_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_user_recent_playlists WHERE user_id = %s ORDER BY timestamp ASC;", (user_id, ))
    return cursor.fetchone()

def retrieveRecentPlaylists():
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT playlist_id FROM mixtape_fm_user_recent_playlists;")
    return cursor.fetchall()

def getRecentPlaylists(n):
  recent_playlist_ids = retrieveRecentPlaylists()
  if (len(recent_playlist_ids) > n):
    recent_playlist_ids = recent_playlist_ids[0:n+1]
  db_playlists = []
  for playlist_id in recent_playlist_ids:
    db_playlist = get_playlist_from_playlist_id(playlist_id)
    db_playlists.append(db_playlist[0])
    # db_playlists.append(get_playlist_from_playlist_id(playlist_id))
  playlists = get_playlists_from_results(db_playlists)
  return playlists
  # return jsonify(playlists)

def getUserPlaylists(user_id):
  if (user_id == None or user_id == ""):
    return []
    # return jsonify([])
  db_playlists = get_user_playlists(user_id)
  print("getUserPlaylists")
  print(db_playlists)
  if (db_playlists == []):
    return []
    # return jsonify([])
  playlists = get_playlists_from_results(db_playlists)
  return playlists
  # return jsonify(playlists)

## HELPER TO RETRIEVE COMMENTS
def get_comments(playlist_id):
  if (playlist_id == None):
    return []
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_comments WHERE playlist_id = %s;", (playlist_id, ))
    # cursor.execute("SELECT * FROM mixtape_fm_comments WHERE playlist_id = %s ORDER BY stars DESC;", (playlist_id, ))
    return cursor.fetchall()

def format_db_comments(db_comments):
  comments = []
  for comment in db_comments:
    commenter_id = comment[1]
    commenter = getUserFromUserId(commenter_id)
    commenter_text = comment[3]
    comments.append({'commenterID': commenter_id, 'commenterPFP': commenter[5], 'commentText': commenter_text})
  return comments

def getComments(playlist_id):
  if (playlist_id == None or playlist_id == ''):
    return []
    # return jsonify([])
  db_comments = get_comments(playlist_id)
  comments = format_db_comments(db_comments)
  print("comments= " + str(comments))
  return comments
  # return jsonify(comments)

def get_ratings(user_id, playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_ratings WHERE rating_user_id=%s AND playlist_id=%s;", (user_id, playlist_id))
    return cursor.fetchall()    

def get_ratings_no_user(playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_ratings WHERE playlist_id=%s;", (playlist_id, ))
    return cursor.fetchall()  

def get_all_ratings(playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_ratings WHERE playlist_id=%s;", (playlist_id, ))
    return cursor.fetchall()    

def get_ratings_from_db_ratings(db_ratings):
  ratings = []
  if (db_ratings):
    for db_rating in db_ratings:
      user = getUserFromUserId(db_rating[1])
      rating = {'raterID':user[0], 'raterPFP':user[5], 'rating':db_rating[3]}
      ratings.append(rating)
  return ratings

# def getRatings(playlist_id):
#   ratings = []
#   if (playlist_id == None):
#     return ratings
#     # return jsonify(ratings)
#   db_ratings = get_ratings(playlist_id)
#   ratings = get_ratings_from_db_ratings(db_ratings)
#   return ratings
#   # return jsonify(ratings) 

def getRatings(user_id, playlist_id):
  ratings = []
  if (playlist_id == None or user_id == None):
    return ratings
    # return jsonify(ratings)
  db_ratings = get_ratings(user_id, playlist_id)
  ratings = get_ratings_from_db_ratings(db_ratings)
  return ratings
  # return jsonify(ratings) 

def getAllRatings(playlist_id):
  ratings = []
  if (playlist_id == None):
    return ratings
    # return jsonify(ratings)
  db_ratings = get_all_ratings(playlist_id)
  ratings = get_ratings_from_db_ratings(db_ratings)
  return ratings
  # return jsonify(ratings)


### *************************************************************************************
### *************************************************************************************
### ******************************SETTER / INSERT FUNCTIONS******************************
### *************************************************************************************
### *************************************************************************************

def insert_playlist(user_id, playlist_name, image):
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_playlists (user_id, playlist_name, creation_date, image) VALUES (%s, %s, CURRENT_TIMESTAMP, %s);", \
    (user_id, playlist_name, image))
  playlist_id = get_playlist_id(user_id, playlist_name)
  return playlist_id[0]

def insert_song_into_playlist(playlist_id, song_id, position):
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_playlist_songs (playlist_id, song_id, position) VALUES (%s, %s, %s);", (playlist_id, song_id, position))
  p_s_id = get_playlist_song_id(playlist_id, song_id)
  return p_s_id[0]

def insert_song(name, artist, album, genre, duration, image):
  if (name == None or artist == None or album == None or duration == None):
    print("Invalid parameters:")
    print("  name= " + str(name))
    print("  artist= " + str(artist))
    print("  album= " + str(album))
    print("  duration= " + str(duration))
    return None
  if (get_song_id(name, artist, album, genre, duration, image) == None):
    with get_db_cursor(True) as cursor:
      if (genre == None and image != None):
        cursor.execute("INSERT INTO mixtape_fm_songs (name, artist, album, duration, image) VALUES (%s, %s, %s, %s, %s);", \
        (name, artist, album, duration, image))
      elif (genre != None and image == None):
        cursor.execute("INSERT INTO mixtape_fm_songs (name, artist, album, genre, duration) VALUES (%s, %s, %s, %s, %s);", \
        (name, artist, album, genre, duration))
      elif (genre == None and image == None):
        cursor.execute("INSERT INTO mixtape_fm_songs (name, artist, album, duration) VALUES (%s, %s, %s, %s);", \
        (name, artist, album, duration))
      else:
        cursor.execute("INSERT INTO mixtape_fm_songs (name, artist, album, genre, duration, image) VALUES (%s, %s, %s, %s, %s, %s);", \
        (name, artist, album, genre, duration, image))
  s_id = get_song_id(name, artist, album, genre, duration)
  return s_id[0]

def insertSong(name, artist, album, genre, duration, image):
  if (name == None or artist == None or album == None or duration == None):
    print("Invalid parameters:")
    print("  name= " + str(name))
    print("  artist= " + str(artist))
    print("  album= " + str(album))
    print("  duration= " + str(duration))
    return None
  if (get_song_id(name, artist, album, genre, duration, image) == None):
    with get_db_cursor(True) as cursor:
      if (genre == None and image != None):
        cursor.execute("INSERT INTO mixtape_fm_songs (name, artist, album, duration, image) VALUES (%s, %s, %s, %s, %s);", \
        (name, artist, album, duration, image))
      elif (genre != None and image == None):
        cursor.execute("INSERT INTO mixtape_fm_songs (name, artist, album, genre, duration) VALUES (%s, %s, %s, %s, %s);", \
        (name, artist, album, genre, duration))
      elif (genre == None and image == None):
        cursor.execute("INSERT INTO mixtape_fm_songs (name, artist, album, duration) VALUES (%s, %s, %s, %s);", \
        (name, artist, album, duration))
      else:
        cursor.execute("INSERT INTO mixtape_fm_songs (name, artist, album, genre, duration, image) VALUES (%s, %s, %s, %s, %s, %s);", \
        (name, artist, album, genre, duration, image))
  s_id = get_song_id(name, artist, album, genre, duration, image)
  return s_id[0]

# def insert_new_user(user_id):
#   with get_db_cursor(True) as cursor:
#     cursor.execute("INSERT INTO mixtape_fm_users (user_id, spotify_linked) VALUES (%s, %s);", (user_id, 'FALSE'))
#     return

# def insertNewComment(commenter_id, playlist_id, stars, content):
#   # if (stars < 1 or stars > 5):
#   #   print("Invalid number of stars in review")
#   #   return None
#   if (get_comment(commenter_id, playlist_id) != []):
#     print("User has already left a review of this playlist")
#     return None
#   with get_db_cursor(True) as cursor:
#     if (stars == '' and content != ''):
#       cursor.execute("INSERT INTO mixtape_fm_comments (comment_user_id, playlist_id, content, timestamp) VALUES (%s, %s, %s, CURRENT_TIMESTAMP);", \
#       (commenter_id, playlist_id, content))
#     elif (content == '' and stars != ''):
#       cursor.execute("INSERT INTO mixtape_fm_comments (comment_user_id, playlist_id, stars, timestamp) VALUES (%s, %s, %s, CURRENT_TIMESTAMP);", \
#       (commenter_id, playlist_id, stars))
#     else:
#       cursor.execute("INSERT INTO mixtape_fm_comments (comment_user_id, playlist_id, stars, content, timestamp) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP);", \
#       (commenter_id, playlist_id, stars, content))
#     return get_comment(commenter_id, playlist_id)

def insert_tag(tag_name):
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_tags (tag_name) VALUES (%s);", (tag_name,))
  t_id = get_tag_id(tag_name)
  return t_id[0]

def insert_playlist_tag_id(playlist_id, tag_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_playlist_tags (playlist_id, tag_id) VALUES (%s, %s);", (playlist_id, tag_id))
  return

def insert_playlist_tag(playlist_id, tag_name):
  tag_id = get_tag_id(tag_name)
  if (tag_id is None):
    tag_id = insert_tag(tag_name)
  insert_playlist_tag_id(playlist_id, tag_id)
  return

def removePlaylistLeastRecent(user_id, playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("DELETE FROM mixtape_fm_user_recent_playlists WHERE user_id = %s AND playlist_id = %s;", (user_id, playlist_id))
  return

def deletePlaylistRecent(user_id):
  least_recent = playlistLeastRecent(user_id)
  removePlaylistLeastRecent(least_recent[0], least_recent[1])
  return

def addPlaylistToRecent(user_id, playlist_id):
  if (isPlaylistRecent(user_id, playlist_id) == []):
    if (getNumPlaylistRecents(user_id) > 10):
      deletePlaylistRecent(user_id)
    insertPlaylistRecent(user_id, playlist_id)
  else:
    updatePlaylistRecent(user_id, playlist_id)
  return

def check_ratings(user_id, playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_ratings WHERE rating_user_id=%s AND playlist_id=%s;", (user_id, playlist_id))
    return cursor.fetchall()

def updateRatings(user_id, playlist_id, rating, updating=False):
  with get_db_cursor(True) as cursor:
    if (updating):
      cursor.execute("UPDATE mixtape_fm_ratings SET stars=%s WHERE rating_user_id=%s AND playlist_id=%s;", \
      (rating, user_id, playlist_id))
    else:
      cursor.execute("INSERT INTO mixtape_fm_ratings (rating_user_id, playlist_id, stars, timestamp) VALUES (%s, %s, %s, CURRENT_TIMESTAMP);", \
      (user_id, playlist_id, rating))
  return

def ratePlaylist(user_id, playlist_id, rating):
  if (user_id == None or playlist_id == None or rating == None):
    print("Invalid parameters:")
    print("  user_id= " + str(user_id))
    print("  playlist_id= " + str(playlist_id))
    print("  rating= " + str(rating))
    return
  if (rating < 1 or rating > 5):
    print("Invalid rating of " + str(rating) + " stars")
    return
  if (check_ratings(user_id, playlist_id) != []):
    updateRatings(user_id, playlist_id, rating, True)
  else:
    updateRatings(user_id, playlist_id, rating, False)
  return

def insert_comment(user_id, playlist_id, comment):
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_comments (comment_user_id, playlist_id, content, timestamp) VALUES (%s, %s, %s, CURRENT_TIMESTAMP);", \
    (user_id, playlist_id, comment))
  return

def addComment(user_id, playlist_id, comment):
  if (user_id == None or playlist_id == None or comment == None):
    print("Invalid parameters:")
    print("  user_id= " + str(user_id))
    print("  playlist_id= " + str(playlist_id))
    print("  comment= " + str(comment))
    return
  insert_comment(user_id, playlist_id, comment)
  return

def deleteRating(user_id, playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("DELETE * FROM mixtape_fm_ratings WHERE rating_user_id=%s AND playlist_id=%s;", \
    (user_id, playlist_id))
  return

def deleteComment(user_id, playlist_id, comment):
  with get_db_cursor(True) as cursor:
    cursor.execute("DELETE FROM mixtape_fm_comments WHERE comment_user_id=%s AND playlist_id=%s AND content=%s;", \
    (user_id, playlist_id, comment))
  return

def deleteComments(user_id, playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("DELETE FROM mixtape_fm_comments WHERE comment_user_id=%s AND playlist_id=%s;", \
    (user_id, playlist_id))
  return

def create_playlist(user_id, playlist_name, image):
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_playlists (user_id, playlist_name, creation_date, image) VALUES (%s, %s, CURRENT_TIMESTAMP, %s);",
    (user_id, playlist_name, image))
  return

def createPlaylist(user_id, playlist_name, image, song_ids):
  if (user_id == None or playlist_name == None):
    print("Invalid parameters")
    print("  user_id= " + str(user_id))
    print("  playlist_name= " + str(playlist_name))
    return None
  if (check_playlists(user_id, playlist_name) != []):
    print("Playlist already exists for user_id= %s, playlist_name= %s" % (user_id, playlist_name))
    return None
  create_playlist(user_id, playlist_name, image)
  p_id = get_playlist_id(user_id, playlist_name)
  playlist_id = p_id[0]
  position = 0
  for song_id in song_ids:
    insert_song_into_playlist(playlist_id, song_id, position)
    position += 1
  return playlist_id

def delete_song(playlist_id, song_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("DELETE FROM mixtape_fm_playlist_songs WHERE playlist_id=%s AND song_id=%s;", \
    (playlist_id, song_id))
  return

def deleteSongs(user_id, playlist_id, song_ids):
  if (user_id == None or playlist_id == None or song_ids == []):
    print("Invalid parameters")
    print("  user_id= " + str(user_id))
    print("  playlist_id= " + str(playlist_id))
    print("  song_ids= " + str(song_ids))
    return None
  for song_id in song_ids:
    if (song_id != None):
      delete_song(playlist_id, song_id)
  return playlist_id

def delete_playlist_songs(playlist_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("DELETE FROM mixtape_fm_playlist_songs WHERE playlist_id=%s;", (playlist_id, ))
  return

def update_playlist(user_id, playlist_id, playlist_name, playlist_image=None):
  with get_db_cursor(True) as cursor:
    if (playlist_image == None):
      cursor.execute("UPDATE mixtape_fm_playlists SET playlist_name=%s WHERE user_id=%s AND playlist_id=%s;", \
      (playlist_name, user_id, playlist_id))
    else:
      cursor.execute("UPDATE mixtape_fm_playlists SET playlist_name=%s, image=%s WHERE user_id=%s AND playlist_id=%s;", \
      (playlist_name, playlist_image, user_id, playlist_id))
  return


# def updatePlaylist(user_id, playlist_id, added_song_ids, deleted_song_ids, playlist_name, playlist_image):
def updatePlaylist(user_id, playlist_id, song_ids, playlist_name, playlist_image):
  if (user_id == None or playlist_id == None or playlist_name == None or song_ids == []):
    print("Invalid parameters")
    print("  user_id= " + str(user_id))
    print("  playlist_id= " + str(playlist_id))
    print("  playlist_name= " + str(playlist_name))
    print("  song_ids= " + str(song_ids))
    return None
  delete_playlist_songs(playlist_id)
  if (playlist_image == None):
    update_playlist(user_id, playlist_id, playlist_name)
  else:
    update_playlist(user_id, playlist_id, playlist_name, playlist_image)
  position = 0
  for song_id in song_ids:
    insert_song_into_playlist(playlist_id, song_id, position)
    position += 1
  return playlist_id


def add_tag(tag_name):
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_tags (tag_name) VALUES (%s);", (tag_name, ))
  return

def addTag(tag_name):
  if (tag_name == None):
    print("Invalid tag_name= " + str(tag_name))
    return None
  if (check_tag_exists(tag_name) != []):
    return get_tag_id(tag_name)
  else:
    add_tag(tag_name)
    return get_tag_id(tag_name)

# POST savePlaylist(userID, playlistID): so we can keep track of the user’s saved playlists
def savePlaylist(user_id, playlist_id):
  if (user_id == None or playlist_id == None):
    print("Invalid parameters:")
    print("  user_id= " + str(user_id))
    print("  playlist_id= " + str(playlist_id))
    return
  with get_db_cursor(True) as cursor:
    cursor.execute("INSERT INTO mixtape_fm_playlists_saved (playlist_id, user_id) VALUES (%s, %s);", (playlist_id, user_id))
  return

def get_saved_playlists(user_id):
  with get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_playlists_saved WHERE user_id = %s;", (user_id, ))
    return cursor.fetchall()

def getSavedPlaylists(user_id):
  if (user_id == None):
    print("Invalid parameter:")
    print("  user_id= " + str(user_id))
    return
  playlist_results = get_saved_playlists(user_id)
  playlists = get_playlists_from_results(playlist_results)
  return playlists
  # return jsonify(playlists)

def unsavePlaylist(user_id, playlist_id):
  if (user_id == None or playlist_id == None):
    print("Invalid parameters:")
    print("  user_id= " + str(user_id))
    print("  playlist_id= " + str(playlist_id))
    return
  with get_db_cursor(True) as cursor:
    cursor.execute("DELETE FROM mixtape_fm_playlists_saved WHERE playlist_id=%s AND user_id=%s;", (playlist_id, user_id))
  return
  