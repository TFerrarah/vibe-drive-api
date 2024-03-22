##################
# API Endpoint testing
##################

from fastapi import FastAPI
from fastapi.responses import FileResponse

import songBuilder

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

##################
# Cloud Endpoints
##################


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

# Get Separated song
@app.get("/song/{song_id}")
async def get_song(song_id: str):
    # Get a single song
    song = spotify_api.fetch_song(song_id)
    # Separate song
    song_separated = songBuilder.build_song(song)
    # return file
    return FileResponse(song_separated)


import uvicorn
import os

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))