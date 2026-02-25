# MGL7361 – Availability Proof of Concept

## Project Description

This project demonstrates availability tactics using a simple Flask-based microservice architecture.  
The system follows a Primary–Spare redundancy pattern with failure detection and automatic recovery.

## Architecture

The system is composed of:

- Primary Service  
- Spare Service  
- Load Balancer  
- Failure Detection Mechanism (Monitor)

More details are available in `docs/architecture.md`.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Option A – one-liner (runs all 3 services in background)
chmod +x run.sh && ./run.sh

# Option B – manual (3 separate terminals)
python primary/app.py   # port 5001
python spare/app.py     # port 5002
python balancer/app.py  # port 5000
```

## Demo – Failure & Failover Scenario

```bash
# 1. Verify primary is serving traffic
curl http://localhost:5000/data           # → {"service": "primary", ...}

# 2. Check load-balancer state
curl http://localhost:5000/status         # → primary_healthy: true

# 3. Inject failure into Primary
curl -X POST http://localhost:5001/fail   # monitor detects within ~3s

# 4. Traffic is now routed to Spare
curl http://localhost:5000/data           # → {"service": "spare", ...}

# 5. Recover Primary
curl -X POST http://localhost:5001/recover

# 6. Traffic routes back to Primary automatically
curl http://localhost:5000/data           # → {"service": "primary", ...}
```

## Project Structure

```
.
├── primary/
│   └── app.py          # Primary service (port 5001) – /data, /health, /fail, /recover
├── spare/
│   └── app.py          # Spare service (port 5002) – /data, /health
├── balancer/
│   └── app.py          # Load balancer + monitor (port 5000) – /data, /health, /status
├── docs/
│   └── architecture.md # Architecture documentation
├── requirements.txt
└── run.sh              # Convenience startup script
```

## Authors

- Nisrine Arrachid – System architecture, repository structure and documentation  
- Ilyes Khayati – Implementation of Primary and Spare services (/data, /health)  
- Thomas Veneroso – Failure simulation and interface  
- Eldrick Beaumont – Failure detection (monitor) and metrics
