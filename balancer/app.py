# Balancer
from flask import Flask, request
from flask_cors import CORS
import json
import requests
import os
import time

app = Flask(__name__)
CORS(app)

PORT = int(os.getenv("PORT", "5000"))
#LOG_PATH = os.path.join(".. ","log","log.txt")
LOG_PATH = os.path.join("log","log.txt")
print(LOG_PATH)

PRIMARY = {"name": "PRIMARY", "port": int(os.getenv("PORT", "5001"))}
SPARE = {"name": "SPARE", "port": int(os.getenv("PORT", "5002"))}
ACTIVE = PRIMARY

def flipServer():
    global ACTIVE
    if ACTIVE == PRIMARY:
        ACTIVE = SPARE
    else:
        ACTIVE = PRIMARY
        
def logRoute(path, serverName,response, response_code):
    curTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    response = response.decode('utf-8') if isinstance(response, bytes) else str(response)
    
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            pass
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps({"timestamp": curTime, "route": path, "sent_to": serverName, "response": response, "code": response_code}) + "\n")
    print(json.dumps({"timestamp": curTime, "route": path, "sent_to": serverName, "response": response, "code": response_code}))

@app.route('/', defaults={'path': ''}, methods=["GET", "POST"])
@app.route('/<path:path>', methods=["GET", "POST"])
def routing(path):
    url = f"http://localhost:{ACTIVE['port']}/{path}"
    method = request.method
    returnText = ""
    code = None
    serverSent = ACTIVE['name']
    
    
    if path == "activateSpare":
        #Activate non active server
        flipServer()
        returnText = f"success: {ACTIVE['name']} is activated"
        code = 200
        serverSent = "NONE"
    elif path == "revive":
        #Revive non active server
        response = ""
        if ACTIVE == PRIMARY:
            response = requests.post(f"http://localhost:{SPARE['port']}/revive")
            serverSent = SPARE['name']
        else:
            response = requests.post(f"http://localhost:{PRIMARY['port']}/revive")
            serverSent = PRIMARY['name']
        returnText = response.content
        code = response.status_code
    else:
        #Route to active server
        try:
            response = requests.request(method, url, timeout=1)
            returnText = response.content
            code = response.status_code
        except requests.exceptions.RequestException:
            returnText = "error: Service unavailable"
            code = 503
    
    logRoute(path, serverSent, returnText, code)
    return returnText, code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)