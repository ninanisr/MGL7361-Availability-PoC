"""
Primary Service – MGL7361 Availability PoC
Runs on port 5001.
Exposes:
  GET /health   → returns {"status": "ok", "service": "primary"}
  GET /data     → returns a sample data payload
  POST /fail    → injects a simulated failure (sets the service unhealthy)
  POST /recover → restores the service to a healthy state
"""

from flask import Flask, jsonify
import time

app = Flask(__name__)

# Mutable state flag – simulates an injected failure
_healthy = True


@app.route("/health")
def health():
    """Health-check endpoint used by the watchdog."""
    if _healthy:
        return jsonify({"status": "ok", "service": "primary"}), 200
    return jsonify({"status": "error", "service": "primary", "reason": "simulated failure"}), 500


@app.route("/data")
def data():
    """Returns a sample business-data payload."""
    if not _healthy:
        return jsonify({"error": "Primary service is unavailable"}), 500
    return jsonify({
        "service": "primary",
        "timestamp": time.time(),
        "message": "Hello from the Primary service!",
        "items": [
            {"id": 1, "value": "alpha"},
            {"id": 2, "value": "beta"},
            {"id": 3, "value": "gamma"},
        ],
    }), 200


@app.route("/fail", methods=["POST"])
def fail():
    """Injects a failure – the service starts returning HTTP 500."""
    global _healthy
    _healthy = False
    return jsonify({"message": "Failure injected – primary is now unhealthy"}), 200


@app.route("/recover", methods=["POST"])
def recover():
    """Clears the injected failure."""
    global _healthy
    _healthy = True
    return jsonify({"message": "Primary recovered – now healthy again"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
