from fastapi import APIRouter, HTTPException, Request, Response
from utils.firebase import db
from database.models.playlist import Playlist
from pydantic import BaseModel
from database.dummydata import dummy_songs
from utils import spotify
from fastapi.responses import JSONResponse
import spotipy

class UserInput(BaseModel):
    query: str
    
class Song(BaseModel):
    title: str
    artist: str
    
class Tracks(BaseModel):
    tracks: list[Song]
        
    
router = APIRouter()

# Process query string, feed into langchain, get list of tracks.
@router.post("/")
def show_playlist(tracks: Tracks, request: Request, response: Response):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    if not access_token or not refresh_token:
        raise HTTPException(status_code=400, detail="Authentication required")
    
    sp = spotify.get_spotify_client(access_token) 
    
    tracks = [track.model_dump() for track in tracks.tracks] 

    playlist_tracks = []
    
    for track in tracks:
        search_query = f"track:{track['title']} artist:{track['artist']}"
        
        try:
            searched_track = sp.search(q=search_query, limit=1, type="track")  
            
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 401: 
                new_token = spotify.refresh_token(refresh_token)
                if not new_token:
                    raise HTTPException(status_code=400, detail="Authentication required, login again")

                response.set_cookie(key="access_token", value=new_token['access_token'])
                response.set_cookie(key="refresh_token", value=new_token['refresh_token'])
                sp = spotify.get_spotify_client(new_token["access_token"]) 

                searched_track = sp.search(q=search_query, limit=1, type="track") 
        
        if searched_track and searched_track["tracks"]["items"]:
            track_model = {
                "name": searched_track["tracks"]["items"][0]["name"],
                "artist": searched_track["tracks"]["items"][0]["artists"][0]["name"],
                "album": searched_track["tracks"]["items"][0]["album"]["name"],
                "image": searched_track["tracks"]["items"][0]["album"]["images"][2]["url"],
                "uri": searched_track["tracks"]["items"][0]["uri"]
            }
            playlist_tracks.append(track_model) 
    
    return JSONResponse(content={"message": "Playlist created successfully", "songs": playlist_tracks})




