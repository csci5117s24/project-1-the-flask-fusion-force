from flask import session
from os import environ as env
from datetime import datetime, timedelta
import base64
import requests
import json
import time
import db

redirect_uri = "http://127.0.0.1:5000/spotify/callback"

def base64_client_creds():
  credentials_str = f"{env['SPOTIFY_CLIENT_ID']}:{env['SPOTIFY_CLIENT_SECRET']}"
  credentials_bytes = credentials_str.encode('ascii')

  base64_bytes = base64.b64encode(credentials_bytes)
  return base64_bytes.decode("ascii")

def process_spotify_tokens(response_json):
  user_id = get_user_info(response_json["access_token"]).get('id')
                # if session['spotify'] is None else session['spotify']['user_id']
  spotify = {
    "user_id": user_id,
    "access_token": response_json["access_token"],
    "refresh_token": response_json["refresh_token"],
    "expire_time": datetime.now() + timedelta(seconds=response_json["expires_in"]),
  }
  session['spotify'] = spotify

  db_update_tokens(user_id, spotify['access_token'], spotify['refresh_token'])
  # potential bug: if spotify token expire time changes

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
  response = requests.post(url='https://accounts.spotify.com/api/token', data=data, headers=auth_options)
  response_json = json.loads(response.content)
  process_spotify_tokens(response_json)
  return session['spotify']['user_id']

# Returns user json object concerning their Spotify Account
def get_user_info(access_token):
   user_url = "https://api.spotify.com/v1/me"
   user_headers = {'Authorization': 'Bearer ' + access_token}
#    user_rsp = requests.get(url=user_url, headers=user_headers)
#    print(user_rsp.url)
#    print(user_rsp.reason)
#    print(user_rsp.headers)
#    print(user_rsp.content)
#    print(json.loads(user_rsp.content))
   return json.loads(user_rsp.content)

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

def if_expired_refresh_token():
  # Check if need refresh
  spotify = session["spotify"]
  if spotify["expire_time"] < time.time():
    return

  print(f"refreshing token for user {spotify['user_id']}...")
  auth_options = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ' + base64_client_creds()
  }

  body = {
    "refresh_token": spotify["refresh_token"],
    "grant_type": 'refresh_token'
  }

  response = requests.post(url='https://accounts.spotify.com/api/token', data=body, headers=auth_options)
  response_json = response.json()
  process_spotify_tokens(response_json)

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