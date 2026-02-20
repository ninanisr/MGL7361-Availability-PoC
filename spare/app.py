# Spare service
from flask import Flask, jsonify
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)

ROLE = "spare"
PORT = int(os.getenv("PORT", "5002"))

state = {"down": False, "down_since": None}

@app.get("/health")
def health():
    if state["down"]:
        return jsonify({"role": ROLE, "status": "DOWN"}), 500
    return jsonify({"role": ROLE, "status": "UP"}), 200

@app.get("/data")
def data():
    if state["down"]:
        return jsonify({"role": ROLE, "error": "Service is DOWN"}), 500
    return jsonify({
        "role": ROLE,
        "status": "OK",
        "data": "hello from spare",
        "ts": time.time()
    }), 200

@app.post("/kill")
def kill():
    state["down"] = True
    state["down_since"] = time.time()
    return jsonify({"ok": True, "role": ROLE, "now": "DOWN"}), 200

@app.post("/revive")
def revive():
    state["down"] = False
    state["down_since"] = None
    return jsonify({"ok": True, "role": ROLE, "now": "UP"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
