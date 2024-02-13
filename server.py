from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def layout():
  return render_template('layout.html.jinja',user_id = 0)

@app.route('/home', methods=['GET'])
@app.route('/homepage', methods=['GET'])
def homepage():
  return render_template('homepage.html.jinja',user_id = 0, playlists = [{'image':'image goes here','name':'playlist name goes here','rating':'rating goes here','tags':['tag1','tag2','tag3']}])
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