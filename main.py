#
# Author: Chloe
# Description: Hosts the flask server for last.fm integration and local dashboard - also starts the RPC process
#
#


# TO-DO
#  - Create dashboard that can toggle RPC on and off

from flask import Flask, render_template, redirect, request, session
import requests
from flask_session import Session
from RPC import RPC_Thread
import multiprocessing
from dotenv import load_dotenv
import os
from hashlib import md5
import json
import tools

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
event = multiprocessing.Event()
rpc_state = False # False = Off, True = On\
rpc_process = None
lastfm_session_key = ""
lastfm_user_name = ""
# This will not stay like this this is just for testing
@app.route("/")
def index():
    global lastfm_session_key
    global lastfm_user_name
    if request.args.get("token"):
        session["lastfm_token"] = request.args.get("token")
        print(request.args.get("token"))
        # We need to send this off to Last.FM to get 
        requestJson = {"token":session["lastfm_token"],"api_key":os.getenv("LASTFM_API_KEY"),"method":"auth.getSession"}
        lastfm_getSession = requests.get("http://ws.audioscrobbler.com/2.0/?"+tools.jsonToString(requestJson))
        session["lastfm_session_key"] = json.loads(lastfm_getSession.text)["session"]["key"]
        lastfm_session_key = json.loads(lastfm_getSession.text)["session"]["key"]
        session["lastfm_user_name"] = json.loads(lastfm_getSession.text)["session"]["name"]
        lastfm_user_name = json.loads(lastfm_getSession.text)["session"]["name"]
        # We are now authenitcated to make requests to the last.fm api
        return redirect('/')
    try:
        if session["lastfm_session_key"] != "":
        # We are authenitcated
            return render_template("home.html")
    except:
        # We are not authenitcated as lastfm_session_key has not yet been set
        return render_template("index.html")
@app.route("/api/lastfm/sign_out")
def lastfm_signout():
    session.pop("lastfm_session_key")
    return redirect('/')

@app.route("/api/lastfm/getTopTracks")
def lastfm_getTopTracks():
    requestJson = {"api_key":str(os.getenv("LASTFM_API_KEY")),"limit":"20","page":"1","user":str(session["lastfm_user_name"]),"method":"library.getartists"}
    lastfm_getArtists = requests.get("http://ws.audioscrobbler.com/2.0/?"+tools.jsonToString(requestJson))
    return {"code":1}

@app.route("/api/lastfm/login", methods=["GET","POST"])
def lastfm_login():
    return redirect("http://www.last.fm/api/auth/?api_key="+os.getenv("LASTFM_API_KEY")+"&cb=http://127.0.0.1:5000", code=302)

@app.route("/api/rpc/now_playing", methods=['GET','POST'])
def rpc_now_playing():
    # We now need to send a request to Last.FM to tell her that we are listening to a song.
    print("req")
    print(lastfm_session_key)
    try:
        if lastfm_session_key != "":
            print("LASTFM - NowPlaying: lastfm linked")
            if request.method == 'POST':
                print("req2")
                data = request.json
                print(data)
                requestJson = {"artist":str(data["artist"]),"track":str(data["track"]),"album":str(data["album"]),"duration":str(data["duration"]),"api_key":str(os.getenv("LASTFM_API_KEY")),"sk":str(lastfm_session_key),"method":"track.updateNowPlaying"}
                requestJson["api_sig"] = tools.lastfm_gen_api_sig(requestJson)
                print(requestJson)
                lastfm_nowplaying = requests.post("http://ws.audioscrobbler.com/2.0/", requestJson)
                print(lastfm_nowplaying.text)
    except Exception as e:
        print(e)
        print("LASTFM - NowPlaying: lastfm not linked")
    
    return 'OK'
@app.route("/api/toggle-rpc", methods=["GET","POST"])
def toggle_rpc():
    global rpc_state
    global event
    global rpc_process
    if rpc_state:
        event.set()
        rpc_process.kill()
    else:
        rpc = multiprocessing.Process(target=RPC_Thread, args=(event,)) #< Note that I did not actually call the function, but instead sent it as a parameter
        
        rpc.start()
        rpc_process = rpc
        print(rpc_process.pid)
        rpc_state = True

    return {"rpc_state":rpc_state}
        


