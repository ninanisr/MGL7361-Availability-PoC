#!/usr/bin/env bash
# run.sh – Start all three services in background processes
# Usage: ./run.sh
# Stop:  kill $(cat .pids)

set -e

PID_FILE=".pids"
> "$PID_FILE"

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Starting Primary service on port 5001..."
python primary/app.py &
echo $! >> "$PID_FILE"

echo "Starting Spare service on port 5002..."
python spare/app.py &
echo $! >> "$PID_FILE"

sleep 1  # Give services a moment to bind

echo "Starting Load Balancer + Watchdog on port 5000..."
python balancer/app.py &
echo $! >> "$PID_FILE"

echo ""
echo "All services started. PIDs saved to $PID_FILE"
echo ""
echo "Try:"
echo "  curl http://localhost:5000/data          # routed to primary"
echo "  curl http://localhost:5000/status        # load-balancer state"
echo "  curl -X POST http://localhost:5001/fail  # inject failure"
echo "  curl http://localhost:5000/data          # now routed to spare"
echo "  curl -X POST http://localhost:5001/recover  # recover primary"
echo ""
echo "Stop all: kill \$(cat $PID_FILE)"
