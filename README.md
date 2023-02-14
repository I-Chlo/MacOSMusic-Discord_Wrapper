# MacOS Music Discord Wrapper

Bascially program flow goes something like this:

- Use AppleScript to expose data about the Music app to python
- Use this data to create the Discord RPC
- At the moment usese the iTunes API to get album art - this may change
    - Caching has been implemented here to reduce the amount of get requests to Apple as well as improving efficiency.

Das about it.  

💅🏻✨ Your welcome ✨💅🏻

&nbsp;
&nbsp;

# Known Issues

- Online interface is bad
    - I know its bad
        - I will fix it
            - When i have time 
- Random crashes due to album art errors
- Flask storing a huge amount of session files
- Last FM token only working if you referesh the webpage then enable rpc
- General Shenanigans

&nbsp;

# To-Do
- Write the program 
- Create my own rich presence wrapper cuz i dont need all the features
- ~~Get Album Artwork for Song~~
- Add Last.Fm Integration
    - Scobbling?
    - Add button to users last.fm page.
- Refactor into Node.Js and use the Discord Game SDK
    - Learn how to use Node.JS
- Make token and session key storage secure
    - See https://martinheinz.dev/blog/59
- ~~move scrobble code to its own function~~

&nbsp;
# Last.FM Integration

What currently works:
- Authentication
    - Auth works but needs to be moved into its own function call. The requests also need to be edited so that they can use json but still turn up as url parameters so the same data can be passed to the url and to the api_sig generation function.
    &nbsp;
    
- Now Playing
    ![alt text](https://github.com/I-Chlo/MacOSMusic-Discord_Wrapper/blob/a16d7ba8950a512481e5b03b8b2cc73e52052407/images/LAST.FM%20-%20Now%20Playing.jpg?raw=true)
    - Every time a new track is played on Apple Music the RPC script sends a POST Request to the Flask server.
    e.g.
        ```
        {'artist': 'Against Me!', 'track': 'Transgender Dysphoria Blues', 'album': 'Transgender Dysphoria Blues', 'duration': 196.399993896484}
        ````
        After this is received the api_key, session key and the method is added to the json
        ```
        requestJson = {"artist":str(data["artist"]),"track":str(data["track"]),"album":str(data["album"]),"duration":str(data["duration"]),"api_key":str(os.getenv("LASTFM_API_KEY")),"sk":str(lastfm_session_key),"method":"track.updateNowPlaying"}
        ```
        Finally this is sent back to LAST.FM as a post request which displays the current song as currently being played, with the below XML being recevied.

        ```
        <lfm status="ok">
        <nowplaying>
            <track corrected="0">Transgender Dysphoria Blues</track>
            <artist corrected="0">Against Me!</artist>
            <album corrected="0">Transgender Dysphoria Blues</album>
            <albumArtist corrected="0"></albumArtist>
            <ignoredMessage code="0"></ignoredMessage>
        </nowplaying>
        </lfm>
        ```
        This returns the data sent and displays if any fields had to be corrected.

- Scrobbling
    - The Scrobbling atm is a bit mid im not gonna lie but it is working... mostly
    - When a track is first played the start time is recorded (in UNIX time)
    - When the song has finished playing the recorded time is subtracked from the current time to get the duration of time the song was listen to
    <br>
    If this is greater than at least of the duration of the song the scrobble is valid and will be submitted to last.fm

    - The majority of the logic is in the RPC.py file as to minimise the communication between the flask and rpc threads

        ```
        <?xml version="1.0" encoding="UTF-8"?>
        <lfm status="ok">
        <scrobbles ignored="0" accepted="1">
            <scrobble>
            <track corrected="0">True Love Knows No Death</track>
            <artist corrected="0">Kele</artist>
            <album corrected="0">The Flames, Pt. 2</album>
            <albumArtist corrected="0"></albumArtist>
            <timestamp>1676402045.7146</timestamp>
            <ignoredMessage code="0"></ignoredMessage>
            </scrobble>
        </scrobbles>
        </lfm>
        ```

        Above is an example of a response from Last.FM after submitting a successful scrobble.
        Again like in the now playing example it will inform you if there are any entry's it had to correct or if the scrobble was rejected.








# Notes

Detect if playhead has been moved / how long the song has been playing for
```
song start:
    set epoch start

song end:
    if start - finish >= track_duration/2 seconds
        scrobbled
    else
        dont
    
```
&nbsp;
&nbsp;

# Libraries Used

- [![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

