# 
# Author: Chloe Hazell
# Description: Some helpful tools
import json
from hashlib import md5
import os
def jsonToString(jsonIn):
    # Takes a json input and converts it into an html parameter string
    # Also generates the api signature
    output = ""
    jsonKeys = jsonIn.keys()
    for key in jsonKeys:
        output += "&" + str(key)+"="+str(jsonIn[key])

    output += "&" + "api_sig=" + lastfm_gen_api_sig(jsonIn) + "&format=json"
    return output


def lastfm_gen_api_sig(data):
    # Use the request data to create a signature and return it to the calling function
    # https://stackoverflow.com/questions/45745836/last-fm-api-invalid-method-signature-but-valid-when-getting-session-key
    api_sig = sorted(data.keys())
    api_sig = [i+data[i] for i in api_sig]
    api_sig = "".join(api_sig) + os.getenv("LASTFM_SECRET_KEY")
    return md5(api_sig.encode()).hexdigest()
