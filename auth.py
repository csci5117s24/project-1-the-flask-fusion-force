import functools
from os import environ as env
from urllib.parse import quote_plus, urlencode
from flask import redirect, current_app, session, url_for, Blueprint
from authlib.integrations.flask_client import OAuth

import db
import spotify

app = Blueprint('auth', __name__)
oauth = None

def setup():
    global oauth
    oauth = OAuth(current_app)

    oauth.register(
        "auth0",
        client_id=env.get("AUTH0_CLIENT_ID"),
        client_secret=env.get("AUTH0_CLIENT_SECRET"),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
    )

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    # Stores user info in the session so we can access the access and refresh tokens
    # Info includes tokens, user_id (.user_info.sub), display name (.userinfo.name)
    token = oauth.auth0.authorize_access_token()
    print(token)
    session["user"] = token
    session["user_id"] = token["userinfo"]["sub"]

    if (db.successfulLoginAttempt(session["user_id"], token["userinfo"])):
        print("****************")
        print("LOGIN SUCCESSFUL")
        print("****************")

        # Fetch spotify info and store in session
        user = db.checkUser(session["user_id"])[0]  # potential bug: what if no users found? is this possible?
        if (not user.get("spotify_access_token") is None): # spotify acc linked
            current_app.logger.info(f'found spotify tokens for logged in user {session["user_id"]}, storing in session...')
            # construct a spotify_session from database to refresh it
            spotify_session = {
                "access_token": user.get("spotify_access_token"),
                "refresh_token": user.get("spotify_refresh_token"),
                "expire_time": user.get("spotify_token_expire")
            }
            session['spotify'] = spotify.refresh_spotify_tokens(session['user_id'], spotify_session)
        return redirect(url_for("homepage"))
    else:
        print("||||||||||||")
        print("LOGIN FAILED")
        print("||||||||||||")
        return redirect(url_for("auth.login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("homepage", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# def require_login(func):
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         if session.get("user") is None:
#             return redirect(url_for("login", next=request.url))
#     return wrapper