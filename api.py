import traceback
from flask import Blueprint, request, Response
import db

app = Blueprint('api', __name__)

def wrapReqChecking(f):
    try:
        ret = f()
    except Exception as e:
        print(traceback.format_exc())
        return Response(status=400, response=getattr(e, 'message', repr(e)), mimetype="text/plain")
    else:
        return ret

def wrapDBFunc(f):
    try:
        f()
    except Exception as e:
        print(traceback.format_exc())
        return Response(status=500, response=getattr(e, 'message', repr(e)), mimetype="text/plain")
    else:
        return Response(status=201, response='test', mimetype="text/plain")

@app.route("/playlist/save", methods=['POST'])
def save_playlist():
    def f():
        json = request.get_json()
        user_id = json['userID']
        playlist_id = json['playlistID']
        return wrapDBFunc(lambda: db.savePlaylist(user_id, playlist_id))
    return wrapReqChecking(f)

@app.route("/playlist/unsave", methods=['POST'])
def unsave_playlist():
    def f():
        json = request.get_json()
        user_id = json['userID']
        playlist_id = json['playlistID']
        #return wrapDBFunc(lambda: db.unsavePlaylist(user_id, playlist_id))
    return wrapReqChecking(f)

@app.route("/playlist/unsave", methods=['POST'])
def rate_playlist():
    def f():
        json = request.get_json()
        user_id = json['userID']
        playlist_id = json['playlistID']
        rating = request.args.get('rating')
        return wrapDBFunc(lambda: db.ratePlaylist(user_id, playlist_id, rating))
    return wrapReqChecking(f)

@app.route("/playlist/comment/add", methods=['POST'])
def add_comment():
    def f():
        json = request.get_json()
        user_id = json['userID']
        playlist_id = json['playlistID']
        commentText = json['commentText']
        return wrapDBFunc(lambda: db.addComment(user_id, playlist_id, commentText))
    return wrapReqChecking(f)

@app.route("/playlist/update", methods=['POST'])
def update_playlist():
    def f():
        json = request.get_json()
        user_id = json['userID']
        playlist_id = json['playlistID']
        song_ids = json['songIDs']
        playlist_name = json['playlistName']
        playlist_image = json['playlistImage']
        return wrapDBFunc(lambda: db.updatePlaylist(user_id, playlist_id, song_ids, playlist_name, playlist_image))
    return wrapReqChecking(f)

@app.route("/playlist/create", methods=['POST'])
def create_playlist():
    def f():
        json = request.get_json()
        user_id = json['userID']
        playlist_name = json['playlistName']
        playlist_image = json['playlistImage']
        song_ids = json['songIDs']
        return wrapDBFunc(lambda: db.createPlaylist(user_id, playlist_name, playlist_image, song_ids))
    return wrapReqChecking(f)