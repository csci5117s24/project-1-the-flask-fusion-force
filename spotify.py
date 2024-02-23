from flask import session
from os import environ as env
import base64
import requests
import time
import db

redirect_uri = "http://127.0.0.1:5000/spotify/callback"

def base64_client_creds():
  credentials_str = f"{env['SPOTIFY_CLIENT_ID']}:{env['SPOTIFY_CLIENT_SECRET']}"
  credentials_bytes = credentials_str.encode('ascii')

  base64_bytes = base64.b64encode(credentials_bytes)
  return base64_bytes.decode("ascii")

def connect_spotify(code):
  auth_options = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ' + base64_client_creds()
  }

  data = {
    "code": code,
    "redirect_uri": redirect_uri,
    "grant_type": 'authorization_code'
  }
  
  # First time login
  # FIXME: Why do I have to login everytime?
  response = requests.post(url='https://accounts.spotify.com/api/token', data=data, headers=auth_options)
  response_json = response.json()
  print(response_json.get('access_token'))
  session['access_token'] = response_json.get('access_token')
  session['refresh_token'] = response_json.get('refresh_token')
  user_json = get_user_info(session['access_token'])
  user_id = user_json.get('id')

  return user_id

# Returns user json object concerning their Spotify Account
def get_user_info(access_token):
   user_url = "https://api.spotify.com/v1/me"
   user_headers = {'Authorization': 'Bearer ' + access_token}
   user_rsp = requests.get(url=user_url, headers=user_headers)
   return user_rsp.json()

# Returns all of the users information on every playlist that they own
def get_playlist_info(access_token):
  playlist_url = "https://api.spotify.com/v1/me/playlists"
  playlist_headers = {'Authorization': 'Bearer ' + access_token}
  playlist_rsp = requests.get(url=playlist_url, headers=playlist_headers)
  playlist_json = playlist_rsp.json()
  # for entry in playlist_json:
  #    print(entry.get("items"))
  # print(playlist_json.get('items'))
  for playlist_info in playlist_json.get('items'):
    print(playlist_info.get('name'))
    print(playlist_info.get('id'))

def if_expired_refresh_token(user_id):
  # Check if need refresh
  # user = session["user"]
  # if user.spotify_expire_time < time.time():
    # return

  auth_options = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ' + base64_client_creds()
  }

  # user_id = get_user_id!!

  # FIXME: get refresh token
  body = {
    "refresh_token": None,#refresh_token,
    "grant_type": 'refresh_token'
  }

  response = requests.post(url='https://accounts.spotify.com/api/token', data=body, headers=auth_options)
  response_json = response.json()
  # Store new tokens in session
  # user.spotify_access_token = response_json.get('access token')
  # user.spotify_refresh_token = response_json.get('refresh token')
  # user.spotify_expire_time = time.time() + 60*60     # in secs

  # db_update_tokens(user_id, user.spotify_access_token, user.spotify_refresh_token))

# db functions
def db_update_tokens(user_id, access_token, refresh_token):
  with db.get_db_cursor(True) as cursor:
    cursor.execute("UPDATE mixtape_fm_users SET spotify_access_token = %s, \
                   spotify_refresh_token = %s, \
                   spotify_token_expire = current_timestamp + interval \'55 minutes\' \
                   where user_id = %s;", \
                    (user_id, access_token, refresh_token))

def db_get_tokens(user_id):
  with db.get_db_cursor(True) as cursor:
    cursor.execute("SELECT * FROM mixtape_fm_users WHERE user_id=%s", (user_id,))
    return cursor.fetchall()