from flask import Flask, request, render_template, redirect, Response
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
import requests
import base64

app = Flask(__name__)
redirect_uri = "http://127.0.0.1:5000/callback"


@app.route('/', methods=['GET'])
def layout():
  return render_template('layout.html.jinja',user_id = 0)

@app.route('/home', methods=['GET'])
@app.route('/homepage', methods=['GET'])
def homepage():
  return render_template('homepage.html.jinja',user_id = 0, playlists = [{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3']}])

@app.route('/login', methods=['GET'])
def login():
  scope = 'user-top-read'
    # Query string is used to retrieve information from a database
  json = {
        "response_type": 'code',
        "client_id": env['SPOTIFY_CLIENT_ID'],
        "scope": scope,
        "redirect_uri": "http://127.0.0.1:5000/callback"
    }
  return redirect('https://accounts.spotify.com/authorize?' +
      urlencode({
        "response_type": 'code',
        "client_id": env['SPOTIFY_CLIENT_ID'],
        "scope": scope,
        "redirect_uri": redirect_uri
    },
    quote_via=quote_plus))

@app.route('/callback', methods=['GET'])
def callback():
  code = request.args.get('code')

  credentials_str = f"{env['SPOTIFY_CLIENT_ID']}:{env['SPOTIFY_CLIENT_SECRET']}"
  credentials_bytes = credentials_str.encode('ascii')

  base64_bytes = base64.b64encode(credentials_bytes)
  base64_str = base64_bytes.decode("ascii")

  auth_options = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': 'Basic ' + base64_str
        }
  
  data = {
    "code": code,
    "redirect_uri": redirect_uri,
    "grant_type": 'authorization_code'
  }
  
  # FIXME: Why do I have to login everytime?
  response = requests.post(url='https://accounts.spotify.com/api/token', data=data, headers=auth_options)
  response_json = response.json()
  access_token = response_json.get('access_token')
  print("Accessing " + str(response_json.get('access_token')))

  playlist_url = "https://api.spotify.com/v1/me/playlists"
  playlist_headers = {'Authorization': 'Bearer ' + access_token}
  playlist_rsp = requests.get(url=playlist_url, headers=playlist_headers)
  playlist_json = playlist_rsp.json()
  print(playlist_json)
  
  return render_template('layout.html')

'''
@app.route('/search', methods=['POST'])
def search():
  return render_template('search.html')

@app.route('/playlist/<int:p_id>', methods=['POST'])
def playlist(p_id):
  return render_template('playlist.html', playlist_id=p_id)

@app.route('/login', methods=['GET'])
def login():
  return render_template('login.html')

@app.route('/settings', methods=['GET'])
def settings():
  return render_template('settings.html')

@app.route('/library/<int:u_id>', methods=['POST'])
def library(u_id):
  return render_template('library.html', user_id=u_id)
'''