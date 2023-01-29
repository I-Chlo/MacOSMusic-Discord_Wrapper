# MacOS Music Discord Wrapper

Bascially program flow goes something like this:

- Use AppleScript to expose data about the Music app to python
- Use this data to create the Discord RPC
- At the moment usese the iTunes API to get album art - this may change
    - Caching has been implemented here to reduce the amount of get requests to Apple as well as improving efficiency.

Das about it.  

&nbsp;
&nbsp;


# To-Do
- Write the program 
- Create my own rich presence wrapper cuz i dont need all the features
- Get Album Artwork for Song
- Add Last.Fm Integration
    - Scobbling?
    - Add button to users last.fm page.
- Refactor into Node.Js and use the Discord Game SDK
    - Learn how to use Node.JS
- Make token and session key storage secure
    - See https://martinheinz.dev/blog/59


# Last.FM Integration

What currently works:
- Authentication
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


Auth works but needs to be moved into its own function call. The requests also need to be edited so that they can use json but still turn up as url parameters so the same data can be passed to the url and to the api_sig generation function.


&nbsp;
&nbsp;

# Libraries Used

- [![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

