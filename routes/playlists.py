from fastapi import APIRouter, HTTPException, Request, Response
from utils.firebase import db
from database.models.playlist import Playlist
from pydantic import BaseModel
from database.dummydata import dummy_songs
from utils import spotify


class UserInput(BaseModel):
    query: str
    
class Tracks(BaseModel):
    tracks: list[dict[str, str]]
        
    
router = APIRouter()

# Process query string, feed into langchain, get list of tracks.
@router.post("/")
def show_playlist(tracks: Tracks, request: Request, response: Response):

    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    
    if not access_token or not refresh_token:
        raise HTTPException(status_code=400, detail="Authentication required")
    
    try:
        sp = spotify.get_spotify_client(access_token)

    except spotify.spotipy.SpotifyException as e:
        if e.http_status == 401:
            new_token = spotify.refresh_token(refresh_token)
            if not new_token:
                raise HTTPException(status_code=400, detail="Authentication required, login again")
            response.set_cookie(key="access_token", value=new_token, httponly=True)
            
            sp = spotify.get_spotify_client(new_token)
    
   
    playlist_tracks = []
    for track in tracks:
        search_query = f"track:{track['name']} artist:{track['artist']}"
        searched_track = sp.search(q=search_query, limit=1, type="track")
        if searched_track:
            playlist_tracks.append(searched_track["tracks"]["items"][0]["uri"])
    return {"message": "Playlist created successfully", "songs": tracks}






