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

def process_spotify_tokens(response_json):
  user_id = get_user_info(response_json["access_token"]).get('id')
                # if session['spotify'] is None else session['spotify']['user_id']
  spotify = {
    "user_id": user_id,
    "access_token": response_json["access_token"],
    "refresh_token": response_json["refresh_token"],
    "expire_time": time.time() + response_json["expires_in"],
  }

  db_update_tokens(user_id, spotify['access_token'], spotify['refresh_token'])
  # potential bug: if spotify token expire time changes
  return spotify

def connect_spotify(code):
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
  return process_spotify_tokens(response_json)

def refresh_spotify_tokens(spotify_session):
  # Check if need refresh
  if spotify_session is None: return
  if time.time() < spotify_session["expire_time"]: return

  print(f"refreshing token for user {spotify_session['user_id']}...")
  auth_options = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ' + base64_client_creds()
  }

  body = {
    "refresh_token": spotify_session["refresh_token"],
    "grant_type": 'refresh_token'
  }

  response = requests.post(url='https://accounts.spotify.com/api/token', data=body, headers=auth_options)
  log_response(response)
  response_json = json.loads(response.content)
  return process_spotify_tokens(response_json)

# Returns user json object concerning their Spotify Account
def get_user_info(access_token):
   user_url = "https://api.spotify.com/v1/me"
   user_headers = {'Authorization': 'Bearer ' + access_token}
   response = requests.get(url=user_url, headers=user_headers)
   log_response(response)
   return json.loads(response.content)

# Returns all of the users information on every playlist that they own
def get_playlist_info(access_token):
  playlist_url = "https://api.spotify.com/v1/me/playlists"
  playlist_headers = {'Authorization': 'Bearer ' + access_token}
  response = requests.get(url=playlist_url, headers=playlist_headers)
  log_response(response)
  playlist_json = response.json()
  # for entry in playlist_json:
  #    print(entry.get("items"))
  # print(playlist_json.get('items'))
  for playlist_info in playlist_json.get('items'):
    print(playlist_info.get('name'))
    print(playlist_info.get('id'))

def search_song(access_token, search_string):
  search_url = "https://api.spotify.com/v1/search?type=track&q=" + requests.utils.quote(search_string)
  search_headers = {'Authorization': 'Bearer ' + access_token}
  response = requests.get(url=search_url, headers=search_headers)
  log_response(response)
  rsp_json = json.loads(response.content)
  return rsp_json

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
  
def log_response(response):
  content = str(response.content)
  print('======response======')
  print(f'''From: {response.url}  Status msg: {response.reason}
Content: {content[:500]}...''') #Headers: {response.headers}
  print('====================')