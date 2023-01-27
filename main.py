#
# Author: Chloe
# Description: Uses Applescript to get data from the music app and then publish it to discord using rich presnese
#

# TO-DO
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


load_dotenv()

cache = dict()
lastalbum = ""
def AppleAPIGet(album):
    # This will get the album data from apple once then cache the result so that i dont keep pinging apple with my shenanigans
    print (album)
    s = shelve.open("apapi_url_cache")
    if album in s:
        print("APPLE API - USING CACHE")
        try:
            return s[album]
        finally:
            s.close()
    else:
        print("APPLE API - NO CACHE FOUND")
        album_sp = album.replace(" ", "%20")
        res = get(url=f"https://itunes.apple.com/search?term={album_sp}&entity=album&country=GB&limit=1")
        res = res.json()
        print(res)
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
    # Osascript runs the script in a terminal. -Ss returns the data as "recompilable" data.
    # Basically just preserves the brackets and quote marks
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

def getAlbumArt(album):
    res = AppleAPIGet(album)
    res = res['results'][0]['artworkUrl100']

    return res

def getAppleMusicURL(album):
    res = AppleAPIGet(album)
    res = res['results'][0]['collectionViewUrl']
    return res




client_id = os.getenv("DISCORD_ID")

RPC = Presence(client_id)
RPC.connect()

print(getCurrentSong())


amdata = ""
rpc_updated_paused = False
while True:
    
    if getPlayerState() != "paused":

        if getCurrentSong() == amdata and rpc_updated_paused == False:
            # There is no need to check more often than this for song updates
            time.sleep(2)
        else:
            # Make sure that we set the program to know that the player is not paused any more
            rpc_updated_paused = False
            # Get the artist name, track name, album name and length of the track
            amdata = getCurrentSong()
            # Using the album name get the artwork
            albimg = getAlbumArt(amdata[2])
            # Update RPC - 
            #   State       - (Artist Name)
            #   Details     - (Song Name)
            #   Large_Image - (Albimg)
            RPC.update(state="by " + amdata[0], details=amdata[1], large_image=albimg, start=time.time(), end=time.time()+float(amdata[3])-float(getPlayerPosition()), buttons=[{"label":"Listen on Apple Music", "url":getAppleMusicURL(amdata[2])}])
    elif rpc_updated_paused == False:
        
        amdata = getCurrentSong()
        albimg = getAlbumArt(amdata[2])
        # The song is currently paused so we want to reflect that in the RPC
        RPC.update(state=amdata[1] + " - " + amdata[0], details=amdata[2], large_image=albimg, small_image="paused", buttons=[{"label":"Listen on Apple Music", "url":getAppleMusicURL(amdata[2])}])
        # The player is currently paused so we set this variable to make sure the RPC reflects that until the player is unpaused
        rpc_updated_paused = True
    
    
    



