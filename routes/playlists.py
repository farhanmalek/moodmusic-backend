from fastapi import APIRouter, HTTPException, Request, Response
from utils.firebase import db
from database.models.playlist import Playlist
from pydantic import BaseModel
from utils import spotify
from fastapi.responses import JSONResponse
import spotipy
from typing import Optional 
import base64
from utils.ai_model import AIModel
from database.models.user import User
import aiohttp
import asyncio   
class Song(BaseModel):
    title: str
    artist: str
    
class PlaylistInput(BaseModel):
    name: str
    artist: str
    album: str
    image: str
    uri: str
class PlaylistInputTracks(BaseModel):
    songs: list[PlaylistInput]


class CreatePlaylistRequest(BaseModel):
    songs: PlaylistInputTracks
    playlist_name: str
    image: Optional[str] = None
    query: Optional[str] = None
   
router = APIRouter()

async def fetch_search_data(session, query):
    try:
        params = {
            "q": query,
            "type": "track",
            "limit": 1
        }
        async with session.get("https://api.spotify.com/v1/search", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "query": query,
                    "status": "success",
                    "tracks": data.get("tracks", {}).get("items", [])
                }
            else:
                return {
                    "query": query,
                    "status": "error",
                    "error": f"HTTP {response.status}"
                }
    except Exception as e:
        return {
            "query": query,
            "status": "error",
            "error": str(e)
        }

# Process query string, feed into langchain, get list of tracks.
@router.get("/search")
async def show_playlist(prompt: str, request: Request, response: Response):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    if not access_token or not refresh_token:
        raise HTTPException(status_code=400, detail="Authentication required")
    
    sp = spotify.get_spotify_client(access_token) 
    
    # use sp instance to get current user, use that id to get users quiz answers.
    try:
        current_user = sp.me()
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401: 
            new_token = spotify.refresh_token(refresh_token)
            if not new_token:
                raise HTTPException(status_code=400, detail="Authentication required, login again")

            response.set_cookie(key="access_token", value=new_token['access_token'])
            response.set_cookie(key="refresh_token", value=new_token['refresh_token'])
            sp = spotify.get_spotify_client(new_token["access_token"]) 

            current_user = sp.me()
    
    current_user_id = current_user["id"]
    user_info: User = db.collection("users").document(current_user_id).get()
    
    if not user_info.exists:
        raise HTTPException(status_code=400, detail="User not found")
    else:
        user = User.from_dict(user_info.to_dict())
        quiz_answers = user.quiz_answers
        
    try:
        model = AIModel(quiz_answers, prompt)
        playlist_tracks = model.get_playlist()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error getting playlist from AI model")
      
    gen_playlist = playlist_tracks["playlist"]
        
    playlist_tracks = []
    search_queries = []
    
    for track in gen_playlist:
        search_query = f"track:{track['title']} artist:{track['artist']}"
        search_queries.append(search_query)
        
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
        
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [fetch_search_data(session, query) for query in search_queries]
        
        results = await asyncio.gather(*tasks)
        
        for result in results:
            if result.get("status") == "success":
                tracks = result.get("tracks", [])
                if not tracks:
                    continue  # Skip if no tracks returned

                track = tracks[0]  # Safe now because we checked if it's empty
                track_model = {
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album": track["album"]["name"],
                    "image": track["album"]["images"][2]["url"] if len(track["album"]["images"]) > 2 else None,
                    "uri": track["uri"]
                }
                playlist_tracks.append(track_model)


    
    return JSONResponse(content={"songs": playlist_tracks})

# create the actual paylist
@router.post("/create")
def create_playlist(
    body: CreatePlaylistRequest,
    request: Request,
    response: Response
):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    if not access_token or not refresh_token:
        raise HTTPException(status_code=400, detail="Authentication required")
    
    sp = spotify.get_spotify_client(access_token)

    try:
        current_user = sp.me()
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            new_token = spotify.refresh_token(refresh_token)
            if not new_token:
                raise HTTPException(status_code=400, detail="Authentication required, login again")

            response.set_cookie(key="access_token", value=new_token['access_token'])
            response.set_cookie(key="refresh_token", value=new_token['refresh_token'])
            sp = spotify.get_spotify_client(new_token["access_token"])
            current_user = sp.me()
    
    current_user_id = current_user["id"]
    
    try:
        new_playlist = sp.user_playlist_create(
            current_user_id,
            name=body.playlist_name,
            public=True,
            collaborative=False,
            description="Generated by MoodMusic"
        )
        
        songs = [song.model_dump() for song in body.songs.songs]
        song_uris = [song["uri"] for song in songs]

        if song_uris:
            sp.playlist_add_items(new_playlist["id"], song_uris)
        else:
            raise HTTPException(status_code=400, detail="No songs added to playlist")

    except spotipy.exceptions.SpotifyException:
        raise HTTPException(status_code=400, detail="Error creating playlist")
    
    if body.image:
        try:
            sp.playlist_upload_cover_image(new_playlist["id"], body.image)
        except spotipy.exceptions.SpotifyException:
            raise HTTPException(status_code=400, detail="Error uploading cover image")
    
    user_ref = db.collection("users").document(current_user_id)
    playlist_ref = user_ref.collection("playlists").document(new_playlist["id"])
    created_playlist = Playlist(name=body.playlist_name, query=body.query, timecreated=None)
    playlist_ref.set(created_playlist.to_dict())
    
    return JSONResponse(content={"status": 201 , "playlist": new_playlist})




