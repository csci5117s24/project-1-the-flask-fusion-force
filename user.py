class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.auth0_access_token = None
        self.auth0_refresh_token = None
        self.auth0_expire_time = None
        self.spotify_access_token = None
        self.spotify_refresh_token = None
        self.spotify_expire_time = None
