####################
#! CLOUD SCRIPT
#? This script is meant to be executed in the cloud
# Song builder 
# Build a single song from a song object
####################

import os
import demucs.separate
import subprocess
import threading
import shlex
import shutil
import time

def new_song(song):
    curr_time = time.time()
    song_id = song["id"]
    yt_dlp_cmd = song["yt_dlp_cmd"]
    print(f"Building song with ID {song_id}")
    # Process new song
    os.mkdir(f"./TMP_{song_id}")
    os.chdir(f"./TMP_{song_id}")
    # Download songs using yt-dlp command
    subprocess.run(yt_dlp_cmd, shell=True)
    #! GPU Intensive workload ahead
    # Separate audio
    MODEL = "htdemucs"
    demucs.separate.main(shlex.split(f'-n {MODEL} -j 2 "./Mix.opus"'))
    # Compress the separated audio using shutil and move it to the Songs folder
    shutil.make_archive(f"../Songs/{song_id}", 'zip', f"./separated/{MODEL}/Mix")
    # Move back to the "Root" directory
    os.chdir("../")
    # Delete the TMP folder with its contents
    shutil.rmtree(f"./TMP_{song_id}")
    # Print message
    print(f"Song with ID {song_id} has been built (Processing time: {time.time() - curr_time} seconds)")

def build_song(song):
    song_id = song["id"]

    # Search song_id.zip in /Songs
    if not os.path.exists(f"./Songs/{song_id}.zip"):
        # Run new_song in a separate thread but return "PROCESSING" to the user
        threading.Thread(target=new_song, args=(song,)).start()
        # Estimated time to separate a song is SONG_LENGTH + 20%
        # Get song length
        song_length = song["duration_ms"]
        eta_seconds = (song_length + (song_length * 0.3)) / 1000
        return eta_seconds
    else:
        print(f"Song with ID {song_id} already exists")
    
    return f"./Songs/{song_id}.zip"