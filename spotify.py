from os import environ as env
import base64
import requests
import json
import time
import db

spotify_redirect_uri = "http://127.0.0.1:5000/spotify/callback"

def base64_client_creds():
  credentials_str = f"{env['SPOTIFY_CLIENT_ID']}:{env['SPOTIFY_CLIENT_SECRET']}"
  credentials_bytes = credentials_str.encode('ascii')

  base64_bytes = base64.b64encode(credentials_bytes)
  return base64_bytes.decode("ascii")

# Given a dict/json of spotify Oauth0 info, store it in session and DB and return an updated version of it(with user id)
# user_id is db user id, not spotify user id
def process_spotify_tokens(user_id, response_json):
  s_user_id = get_user_info(response_json["access_token"]).get('id')

  if 'expire_time' in response_json:
    expire_time = response_json['expire_time']
  else:
    expire_time = calc_expire_time()

  spotify = {
    "user_id": s_user_id,
    "access_token": response_json["access_token"],
    "refresh_token": response_json["refresh_token"],
    "expire_time": expire_time,     # 1 hour
  }

  print(f"storing spotify tokens in DB...")
  db_update_tokens(user_id, spotify['access_token'], spotify['refresh_token'], expire_time)
  # potential bug: if spotify token expire time changes
  return spotify

def connect_spotify(user_id, code):
  auth_options = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ' + base64_client_creds()
  }

  data = {
    "code": code,
    "redirect_uri": spotify_redirect_uri,
    "grant_type": 'authorization_code'
  }

  # First time login
  response = requests.post(url='https://accounts.spotify.com/api/token', data=data, headers=auth_options)
  log_response(response)
  response_json = json.loads(response.content)
  return process_spotify_tokens(user_id, response_json)

# Refresh tokens and return updated version
def refresh_spotify_tokens(user_id, spotify_session):
  # Check if need refresh
  if spotify_session is None: return
  if spotify_session.get("expire_time") is not None and \
    time.time() < spotify_session["expire_time"]: return spotify_session

  print(f"refreshing token for user {user_id}...")
  auth_options = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ' + base64_client_creds()
  }

  body = {
    "refresh_token": spotify_session['refresh_token'],
    "grant_type": 'refresh_token'
  }

  response = requests.post(url='https://accounts.spotify.com/api/token', data=body, headers=auth_options)
  log_response(response,contentMaxLen=1000)
  response_json = json.loads(response.content)
  # for some reason, spotify doesnt send refresh token back, so I have to manually add it
  if (response_json.get('refresh_token') is None):
    response_json['refresh_token'] = spotify_session['refresh_token']
  return process_spotify_tokens(user_id, response_json)

# Returns user json object concerning their Spotify Account
def get_user_info(access_token):
   user_url = "https://api.spotify.com/v1/me"
   user_headers = {'Authorization': 'Bearer ' + access_token}
   response = requests.get(url=user_url, headers=user_headers)
   log_response(response)
   return json.loads(response.content)

# TODO: Hook this to the DB, and call this in connect_spotify
# Returns all of the users information on every playlist that they own
def get_playlist_info(access_token):
  playlist_url = "https://api.spotify.com/v1/me/playlists"
  playlist_headers = {'Authorization': 'Bearer ' + access_token}
  response = requests.get(url=playlist_url, headers=playlist_headers)
  log_response(response)
  playlist_json = response.json()
  return playlist_json

def get_songs_from_playlist(access_token, playlist_id):
  playlist_songs_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
  playlist_songs_headers = {'Authorization': 'Bearer ' + access_token}
  response = requests.get(url=playlist_songs_url, headers=playlist_songs_headers)
  log_response(response)
  playlist_songs_json = response.json()
  # print(playlist_songs_json['items'])
  songs = []
  for song in playlist_songs_json['items']:
    song_id = song['track']['id']
    song_name = song['track']['name']
    song_artist = song['track']['artists'][0]['name']
    song_album = song['track']['album']['name']
    song_duration = song['track']['duration_ms']
    song_image = song['track']['album']['images']
    if (song_image is not None and len(song_image) != 0): song_image = song_image[0].get('url')
    songs.append({"id": song_id, "name": song_name, "artist": song_artist, "album": song_album, "duration": song_duration, "image": song_image})
    # print(song_album)
    # db.insert_song(song_name, song_artist, song_album, None, song_duration)

  return songs


def search_song(access_token, search_string, num_results=20):
  search_url = f"https://api.spotify.com/v1/search?type=track&q={requests.utils.quote(search_string)}&limit={num_results}"
  search_headers = {'Authorization': 'Bearer ' + access_token}
  response = requests.get(url=search_url, headers=search_headers)
  log_response(response, contentMaxLen=1000)
  rsp_json = json.loads(response.content)
  return rsp_json

# db functions
# This user_id is not spotify user_id
# expire_time is epoch time (in int/float)
def db_update_tokens(user_id, access_token, refresh_token, expire_time):
  with db.get_db_cursor(True) as cursor:
    if expire_time is None: 
        expire_time = calc_expire_time()
    cursor.execute(f"UPDATE mixtape_fm_users SET spotify_access_token = %s, \
                   spotify_refresh_token = %s, \
                   spotify_token_expire = %s \
                   where user_id = %s;", \
                    (access_token, refresh_token, expire_time, user_id))

def db_get_tokens(user_id):
  with db.get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_users WHERE user_id=%s", (user_id,))
    return cursor.fetchall()

def calc_expire_time():
  return time.time() + 55*60    # epoch time; 1 hour with leeway

def log_response(response, contentMaxLen=500):
  content = str(response.content)
  print('======response======')
  print(f'''From: {response.url}  Status msg: {response.reason}
Content: {content[:contentMaxLen]}...''') #Headers: {response.headers}
  print('====================')