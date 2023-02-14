# 
"""
 
     _  _        _         _   _                     ____ _     _            
   _| || |_     / \  _   _| |_| |__   ___  _ __ _   / ___| |__ | | ___   ___ 
  |_  ..  _|   / _ \| | | | __| '_ \ / _ \| '__(_) | |   | '_ \| |/ _ \ / _ \
  |_      _|  / ___ \ |_| | |_| | | | (_) | |   _  | |___| | | | | (_) |  __/
    |_||_|   /_/   \_\__,_|\__|_| |_|\___/|_|  (_)  \____|_| |_|_|\___/ \___|
                                                                             
 
"""
# ? Description: Uses Applescript to get data from the music app and then publish it to discord using rich presnese
#

# TODO: 
# - Write the program 
# - Create my own rich presence wrapper cuz i dont need all the features
# - Get Album Artwork for Song



from pypresence import Presence
import time
from subprocess import Popen, PIPE
from requests import get
import shelve
import os
from dotenv import load_dotenv
import logging
import requests
import time



load_dotenv()


cache = dict()
lastalbum = ""
def AppleAPIGet(album, artist):
    # This will get the album data from apple once then cache the result so that i dont keep pinging apple with my shenanigans
    s = shelve.open("apapi_url_cache")
    if album in s:
        print("APPLE API - USING CACHE")
        try:

            return s[album]
        finally:
            s.close()
    else:
        print("APPLE API - NO CACHE FOUND")
        album_sp = album.replace(" ", "%20") + "%20" + artist.replace(" ","%20")
        print(album_sp)
        res = get(url=f"https://itunes.apple.com/search?term={album_sp}&entity=album&country=GB&limit=1")
        res = res.json()
        try:
            s[album] = (res)
        finally:
            s.close()
        print("APPLE API - STORING VALUE IN CACHE")

        return res


def getPlayerPosition():
    cmd = 'tell application "Music" to get player position'
    proc = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    pos, error = proc.communicate(cmd)
    return pos

def getPlayerState():
    cmd = 'tell application "Music" to get player state'
    proc = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    pstate, error = proc.communicate(cmd)

    return pstate.strip() 

def getCurrentSong():
    cmd = 'tell application "Music" to get {artist, name, album, finish} of current track'
    # ! Osascript runs the script in a terminal. -Ss returns the data as "recompilable" data.
    # ! Basically just preserves the brackets and quote marks
    proc = Popen(['osascript', '-ss','-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    prop, error = proc.communicate(cmd)
    # Replace the {} at the start and end of the string with square brackets so that it can
    # be cast to list rather than set
    prop = eval(prop.replace("{","[").replace("}","]"))
    # 0 - Artist Name
    # 1 - Album Name
    # 2 - Song Name
    # 3 - Length of Song
    return prop

def getAlbumArt(amdata):
    res = AppleAPIGet(amdata[2],amdata[0])
   
    res = res['results'][0]['artworkUrl100']

    return res

def getAppleMusicURL(amdata):
    res = AppleAPIGet(amdata[2],amdata[0])
    
    res = res['results'][0]['collectionViewUrl']
    return res


def submit_scrobble(track, artist,album,timestamp,duration):
    requests.post("http://127.0.0.1:5000/api/rpc/scrobble", json={"artist":artist,"track":track,"album":album,"timestamp":timestamp, "duration": duration})


def RPC_Thread(event):
    logging.debug("Running")
    client_id = os.getenv("DISCORD_ID")

    RPC = Presence(client_id)
    RPC.connect()



    amdata = ""
    rpc_updated_paused = False
    start_epoch_time = 0
    end_epoch_time = 0
    last_start_time = 0
    first_song = True

    
    while True:
            if event.is_set():
                 break
            if getPlayerState() != "paused":

                if getCurrentSong() == amdata and rpc_updated_paused == False:
                    # Here we are going to make sure that the song hasn't been skipped / had the playhead moved
                    time.sleep(2)
                else:
                    if start_epoch_time != 0:
                        # A song was playing and no we need to check if we can scroble it
                        if time.time() - start_epoch_time >= (amdata[3]/2):
                            # More than 30 seconds has elapsed since listening to the last song
                            submit_scrobble(amdata[1],amdata[0],amdata[2],start_epoch_time,amdata[3])
                            # The request has now been sent, will be processed by flask
                        else:
                            # The minimum time was not met so the track will not be scrobbled
                            print("LAST.FM SCROBBLER - MINIMUM TIME NOT MET - TRACK WILL NOT BE RECORDED")

                    # Make sure that we set the program to know that the player is not paused any more
                    rpc_updated_paused = False
                    # Get the artist name, track name, album name and length of the track
                    amdata = getCurrentSong()
                    # Using the album name get the artwork
                    albimg = getAlbumArt(amdata)
                    # ! Update RPC - 
                    # *  State       - (Artist Name)
                    # *  Details     - (Song Name)
                    # *  Large_Image - (Albimg)
                    print("DISCORD - Displaying Song")
                    print("PLAYER  - " + str(amdata[1]) + " by " + str(amdata[0]))

                    # Set the time the song started
                    start_epoch_time = time.time()
                    print(start_epoch_time)
                    RPC.update(state="by " + amdata[0], details=amdata[1], large_image=albimg, start=time.time(), end=time.time()+float(amdata[3])-float(getPlayerPosition()), buttons=[{"label":"Listen on Apple Music", "url":getAppleMusicURL(amdata)}])
                    # We need to tell the host that we are playing a new song
                    requests.post("http://127.0.0.1:5000/api/rpc/now_playing", json={"artist":amdata[0],"track":amdata[1],"album":amdata[2],"duration":amdata[3]})

            elif rpc_updated_paused == False:
                start_epoch_time = 0
                amdata = getCurrentSong()
                albimg = getAlbumArt(amdata)
                print("PLAYER - Paused")
                RPC.update(state=amdata[1] + " - " + amdata[0], details=amdata[2], large_image=albimg, small_image="paused", buttons=[{"label":"Listen on Apple Music", "url":getAppleMusicURL(amdata)}])
                # The player is currently paused so we set this variable to make sure the RPC reflects that until the player is unpaused
                rpc_updated_paused = True



    



