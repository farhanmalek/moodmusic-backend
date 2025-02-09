import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

scopes = 'user-read-private user-read-email playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scopes
)

def get_spotify_auth_url():
    return sp_oauth.get_authorize_url()

def parse_response_code(code):
    return sp_oauth.parse_response_code(code)


def get_spotify_token(code):
    return sp_oauth.get_access_token(code)

def get_spotify_client(token):
    return spotipy.Spotify(auth=token)

def refresh_token(token):
    return sp_oauth.refresh_access_token(token)