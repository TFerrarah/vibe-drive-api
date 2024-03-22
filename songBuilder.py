####################
#! CLOUD SCRIPT
#? This script is meant to be executed in the cloud
# Song builder 
# Build a single song from a song object
####################

import os
import demucs.separate
import subprocess
import shlex
import shutil


def build_song(song):
    song_id = song["id"]
    yt_dlp_cmd = song["yt_dlp_cmd"]

    # Search song_id.zip in /Songs
    if not os.path.exists(f"./Songs/{song_id}.zip"):
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
    else:
        print(f"Song with ID {song_id} already exists")
    
    return f"./Songs/{song_id}.zip"