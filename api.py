from flask import Blueprint, request, Response
import db

app = Blueprint('auth', __name__)

@app.route("/playlist/save", method=['POST'])
def save_playlist():
    user_id = request.args.get('userID')
    playlist_id = request.args.get('playlistID')

    db.savePlaylist(user_id, playlist_id)
    return Response(status=201)

@app.route("/playlist/unsave", method=['POST'])
def unsave_playlist():
    user_id = request.args.get('userID')
    playlist_id = request.args.get('playlistID')

    # db.unsavePlaylist(user_id, playlist_id)
    return Response(status=201)

@app.route("/playlist/unsave", method=['POST'])
def rate_playlist():
    user_id = request.args.get('userID')
    playlist_id = request.args.get('playlistID')
    rating = request.args.get('rating')

    db.ratePlaylist(user_id, playlist_id, rating)
    return Response(status=201)

@app.route("/playlist/comment/add", method=['POST'])
def add_comment():
    user_id = request.args.get('userID')
    playlist_id = request.args.get('playlistID')
    commentText = request.args.get('commentText')

    db.addComment(user_id, playlist_id, commentText)
    return Response(status=201)