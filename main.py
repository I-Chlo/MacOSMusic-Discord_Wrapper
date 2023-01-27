#
# Author: Chloe
# Description: Hosts the flask server for last.fm integration and local dashboard - also starts the RPC process
#
#


# TO-DO
#  - Create dashboard that can toggle RPC on and off

from flask import Flask, render_template
from RPC import RPC_Thread
import multiprocessing


app = Flask(__name__)
event = multiprocessing.Event()
rpc_state = False # False = Off, True = On\
rpc_process = None
@app.route("/")
def index():
    return render_template("index.html")


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
        
