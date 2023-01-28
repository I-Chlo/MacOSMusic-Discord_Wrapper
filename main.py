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

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
event = multiprocessing.Event()
rpc_state = False # False = Off, True = On\
rpc_process = None
@app.route("/")
def index():
    if request.args.get("token"):
        session["lastfm_token"] = request.args.get("token")
        print(request.args.get("token"))
        # We need to send this off to Last.FM to get 
        lastfm_getSession = requests.get("http://ws.audioscrobbler.com/2.0/?method=auth.getSession&token="+session["lastfm_token"]
        +"&api_key="+os.getenv("LASTFM_API_KEY")
        +"&api_sig="+lastfm_gen_api_sig({"token":session["lastfm_token"],"api_key":os.getenv("LASTFM_API_KEY"),"method":"auth.getSession"})
        +"&format=json")
        print(lastfm_getSession.url)
        print(lastfm_getSession.text)
        return redirect('/')
    
    return render_template("index.html")

@app.route("/api/lastfm/login", methods=["GET","POST"])
def lastfm_login():
    return redirect("http://www.last.fm/api/auth/?api_key="+os.getenv("LASTFM_API_KEY")+"&cb=http://127.0.0.1:5000", code=302)

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
        


def lastfm_gen_api_sig(data):
    # Use the request data to create a signature and return it to the calling function
    # https://stackoverflow.com/questions/45745836/last-fm-api-invalid-method-signature-but-valid-when-getting-session-key
    api_sig = sorted(data.keys())
    api_sig = [i+data[i] for i in api_sig]
    api_sig = "".join(api_sig) + os.getenv("LASTFM_SECRET_KEY")
    return md5(api_sig.encode()).hexdigest()
