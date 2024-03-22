##################
# API Endpoint testing
##################

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

# SpotiPy Variables
SPOTIFY_CLIENT_ID ="3df6acac572643a09810ac864bbfa08a"
SPOTIFY_CLIENT_SECRET = "2c492ff0333d426a837e418db781a699"
SPOTIFY_REDIRECT_URI = "http://vibedrive.local:8000"

# Spotify API
import spotify
spotify_api = spotify.SpotifyAPI(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# TODO: Remove this endpoint
@app.get("/spotify/login")
async def spotify_login():
    # Get access token
    access_token = spotify_api.get_access_token()
    return {"access_token": access_token}

# Return a list of songs from a playlist
@app.get("/spotify/playlist/{playlist_id}")
async def spotify_playlist(playlist_id: str):
    # Get a list of songs
    songs = spotify_api.fetch_playlist_items(playlist_id)
    return {"songs": songs}

# Return a list of songs from a playlist with audio features
@app.get("/spotify/playlist/{playlist_id}/features")
async def spotify_playlist_features(playlist_id: str):
    # Get a list of songs
    songs = spotify_api.fetch_playlist_items(playlist_id)
    # Get song features from id
    songs_features = spotify_api.audio_features(songs)
    return {"songs": songs_features}

# Return a list of songs from a playlist with audio features and its youtube music link
@app.get("/spotify/playlist/{playlist_id}/ytm")
async def spotify_playlist_ytm(playlist_id: str):
    # Get a list of songs
    songs = spotify_api.fetch_playlist_items(playlist_id)
    # Get song features from id
    songs_features = spotify_api.audio_features(songs)
    # Get YouTube Music link
    songs_ytm = spotify_api.get_ytm_link(songs_features, "./Audio")
    return {"songs": songs_ytm}

# Return a single song object from song ID with audio features and its youtube music link
@app.get("/spotify/song/{song_id}")
async def spotify_song(song_id: str):
    # Get a single song
    song = spotify_api.fetch_song(song_id)
    # Get song features from id
    song_features = spotify_api.audio_features([song])
    # Get YouTube Music link
    song_ytm = spotify_api.get_ytm_link(song_features, "./Audio")
    return {"song": song_ytm}

##################
# Cloud Endpoints
##################

import songBuilder

# Get Separated song
@app.get("/song/{song_id}")
async def get_song(song_id: str):
    # Get a single song
    song = spotify_api.fetch_song(song_id)
    # Separate song
    song_separated = songBuilder.build_song(song)
    # return file
    return FileResponse(song_separated)