"""
Spare Service – MGL7361 Availability PoC
Runs on port 5002.
Mirrors the Primary service endpoints.
Activated automatically by the Load Balancer when the Primary is unhealthy.
"""

from flask import Flask, jsonify
import time

app = Flask(__name__)


@app.route("/health")
def health():
    """Health-check endpoint – the spare is always healthy."""
    return jsonify({"status": "ok", "service": "spare"}), 200


@app.route("/data")
def data():
    """Returns the same shape of data as the Primary service."""
    return jsonify({
        "service": "spare",
        "timestamp": time.time(),
        "message": "Hello from the Spare service (failover active)!",
        "items": [
            {"id": 1, "value": "alpha"},
            {"id": 2, "value": "beta"},
            {"id": 3, "value": "gamma"},
        ],
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)
