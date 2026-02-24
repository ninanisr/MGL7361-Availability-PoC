"""
Load Balancer + Watchdog – MGL7361 Availability PoC
Runs on port 5000.

Responsibilities:
  • Forward client requests to the Primary service (port 5001).
  • Background watchdog polls Primary /health every HEALTH_CHECK_INTERVAL seconds.
  • On failure detection, failover traffic to the Spare service (port 5002).
  • Expose /status to inspect current routing state and metrics.
"""

import threading
import time
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
PRIMARY_URL = "http://localhost:5001"
SPARE_URL   = "http://localhost:5002"
HEALTH_CHECK_INTERVAL = 3   # seconds between health polls
HEALTH_TIMEOUT        = 2   # seconds before a health call is considered failed

# ─────────────────────────────────────────────
# Shared state (protected by a lock)
# ─────────────────────────────────────────────
_lock              = threading.Lock()
_primary_healthy   = True   # current assessment of Primary
_active_backend    = PRIMARY_URL
_failover_count    = 0
_last_check_time   = None
_last_check_status = "unknown"


def _set_active_backend(url: str, is_primary: bool):
    """Switch the active backend and update shared state."""
    global _active_backend, _primary_healthy, _failover_count
    with _lock:
        if is_primary:
            if not _primary_healthy:
                # Recovery
                _primary_healthy = True
                _active_backend  = PRIMARY_URL
                print("[Watchdog] Primary recovered – routing back to primary.")
        else:
            if _primary_healthy:
                # Failover
                _primary_healthy = False
                _active_backend  = SPARE_URL
                _failover_count += 1
                print(f"[Watchdog] Primary FAILED – failing over to spare (event #{_failover_count}).")


def _watchdog():
    """Background thread: periodically checks Primary /health."""
    global _last_check_time, _last_check_status
    while True:
        try:
            resp = requests.get(f"{PRIMARY_URL}/health", timeout=HEALTH_TIMEOUT)
            ok = resp.status_code == 200
            _last_check_status = "healthy" if ok else f"unhealthy (HTTP {resp.status_code})"
            _set_active_backend(PRIMARY_URL, is_primary=ok)
        except requests.exceptions.RequestException as exc:
            _last_check_status = f"unreachable ({exc})"
            _set_active_backend(SPARE_URL, is_primary=False)
        finally:
            with _lock:
                _last_check_time = time.time()
        time.sleep(HEALTH_CHECK_INTERVAL)


# Start watchdog in daemon thread so it exits with the process
_watchdog_thread = threading.Thread(target=_watchdog, daemon=True, name="Watchdog")
_watchdog_thread.start()


# ─────────────────────────────────────────────
# Proxy helpers
# ─────────────────────────────────────────────
PROXIED_ROUTES = ["/data", "/health"]

def _proxy(path: str):
    """Forward the current request to the active backend."""
    with _lock:
        backend = _active_backend

    url = f"{backend}{path}"
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers if k != "Host"},
            data=request.get_data(),
            timeout=5,
        )
        return (resp.content, resp.status_code, dict(resp.headers))
    except requests.exceptions.RequestException as exc:
        return jsonify({"error": "Both backends unreachable", "detail": str(exc)}), 503


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.route("/data", methods=["GET"])
def proxy_data():
    return _proxy("/data")


@app.route("/health", methods=["GET"])
def proxy_health():
    return _proxy("/health")


@app.route("/status", methods=["GET"])
def status():
    """Exposes current load-balancer state and watchdog metrics."""
    with _lock:
        return jsonify({
            "active_backend":    _active_backend,
            "primary_healthy":   _primary_healthy,
            "failover_count":    _failover_count,
            "last_check_time":   _last_check_time,
            "last_check_status": _last_check_status,
        }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
