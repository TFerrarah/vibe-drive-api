####################
# Spotify 
####################

import requests

# SpotiPy
# from spotipy import Spotify, CacheHandler
# from spotipy.oauth2 import SpotifyOAuth

# curl -X POST "https://accounts.spotify.com/api/token" \
#      -H "Content-Type: application/x-www-form-urlencoded" \
#      -d "grant_type=client_credentials&client_id=your-client-id&client_secret=your-client-secret"

class SpotifyAPI:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        # Get access token
        # curl -X POST "https://accounts.spotify.com/api/token" \
        #      -H "Content-Type: application/x-www-form-urlencoded" \
        #      -d "grant_type=client_credentials&client_id=your-client-id&client_secret=your-client-secret"
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        )
        response_data = response.json()
        self.access_token = response_data["access_token"]

    def fetch_playlist_items(self, playlist):
        if not self.access_token:
            raise Exception("Access token not found")

        # Get a list of songs

        # curl --request GET \
        #   --url https://api.spotify.com/v1/playlists/3cEYpjA9oz9GiPac4AsH4n/tracks \
        #   --header 'Authorization: Bearer BQATDwrmpJCr_eB3TVpTPV2VpkOrUK7jycLDAOcpvuOkTCsF1R466CrrmKFmshiQc8uVbCrZZxBycS3PfKYhpW3tw37I4sDPTu-R7iE5yvs-4NcCijI'
        
        offset = 0
        # Spotify Playlists tend to be long.
        # We need to loop trough the playlist items with an offset
        # until we get all the songs

        # We first need to get the total number of songs in the playlist
        response = requests.get(
            f"https://api.spotify.com/v1/playlists/{playlist}/tracks",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            }
        )
        total_songs = response.json()["total"]

        # Now we can loop trough the playlist items
        songs = []
        while offset < total_songs:
            # Be sure to not exceed the limit
            if offset > total_songs:
                offset = total_songs
            response = requests.get(
                f"https://api.spotify.com/v1/playlists/{playlist}/tracks",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                },
                params={
                    "offset": offset,
                    # Only get song id, name, image and artists name
                    "fields": "items(track(id,name,album(images),artists(name)))"
                }
            )
            response_data = response.json()
            # For every song, if there are more than one artists, join them with a comma
            for song in response_data["items"]:
                artists = ""
                for artist in song["track"]["artists"]:
                    artists += artist["name"] + ", "
                artists = artists[:-2]
                songs.append({
                    "id": song["track"]["id"],
                    "image": song["track"]["album"]["images"][0]["url"],
                    "name": song["track"]["name"],
                    "artists": artists,
                    "duration_ms": song["duration_ms"]
                })
            offset += 100
        
        return songs
    
    def fetch_single_song(self, song_id):
        if not self.access_token:
            raise Exception("Access token not found")

        # Get a single song
        response = requests.get(
            f"https://api.spotify.com/v1/tracks/{song_id}",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            }
        )
        response_data = response.json()
        artists = ""
        for artist in response_data["artists"]:
            artists += artist["name"] + ", "
        artists = artists[:-2]
        song = {
            "id": response_data["id"],
            "image": response_data["album"]["images"][0]["url"],
            "name": response_data["name"],
            "artists": artists,
            "duration_ms": response_data["duration_ms"],
        }
        return song

    def audio_features(self, song_objects):
        if not self.access_token:
            raise Exception("Access token not found")

        # Songs objects is a list of song objects just like fetch_playlist_items
        # We need to get the song ids and join them with a comma
        song_ids = []
        for song in song_objects:
            song_ids.append(song["id"])

        # Get song features from id and append "Energy", "Valence" and "Danceability to existing song object along with the average of the three
        # Limit is 50, so we need to loop trough the song ids
        offset = 0
        songs_features = []

        while offset < len(song_ids):
            # Be sure to not exceed the limit
            if offset > len(song_ids):
                offset = len(song_ids)
            response = requests.get(
                "https://api.spotify.com/v1/audio-features",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                },
                params={
                    "ids": ",".join(song_ids[offset:offset+50])
                }
            )
            response_data = response.json()
            for i in range(len(response_data["audio_features"])):
                song = song_objects[offset+i]
                song_features = response_data["audio_features"][i]
                song["energy"] = song_features["energy"]
                song["valence"] = song_features["valence"]
                song["danceability"] = song_features["danceability"]
                song["average"] = (song_features["energy"] + song_features["valence"] + song_features["danceability"])/3
                songs_features.append(song)
            offset += 50

        return songs_features

    def get_ytm_link(self, songs, audio_folder="/home/pi/Songs/Active"):
        # Create yt-dlp command for each song
        # Append the command to every song as a new parameter "yt_dlp_cmd"
        for song in songs:
            # Make folder for song
            # folder_title = f'{audio_folder}/{song["name"]} - {song["artists"]}'.replace(" ", "_")
            # Download the song
            print("Search query: " + f'{song["name"]} {song["artists"]}')

            ####################
            # yt-dlp way
            #TODO: 
            ####################
            yt_dlp_cmd = f'yt-dlp --default-search "https://youtube.com/search?q=" "{song["name"]} by {song["artists"]}" --playlist-items 1 --extract-audio --output "Mix.%(ext)s"'
            song["yt_dlp_cmd"] = yt_dlp_cmd

        return songs
    
    def fetch_song(self, song_id):
        # Use audio_features to get the song object and get_ytm_link to get the youtube music link
        song = self.fetch_single_song(song_id)
        song = self.audio_features([song])[0]
        song = self.get_ytm_link([song])[0]
        return song