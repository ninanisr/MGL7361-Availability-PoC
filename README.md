# MGL7361 – Availability Proof of Concept

## Project Description

This project demonstrates availability tactics using a simple Flask-based microservice architecture.  
The system follows a Primary–Spare redundancy pattern with failure detection and automatic recovery.

## Architecture

The system is composed of:

- Primary Service  
- Spare Service  
- Load Balancer  
- Failure Detection Mechanism (Watchdog)

More details are available in `docs/architecture.md`.

## Authors

- Nisrine Arrachid – System architecture, repository structure and documentation  
- Ilyes Khayati – Implementation of Primary and Spare services (/data, /health)  
- Thomas Veneroso – Failure simulation and interface  
- Eldrick Beaumont – Failure detection (watchdog) and metrics

## Requirements

python3 -m venv .venv
source .venv/bin/activate
pip install flask

## Primary & Spare (Flask)

Deux services Flask identiques (redondance) : **primary** et **spare**.  
Le **watchdog** vérifie `/health` et le **balancer** appelle `/data`.

### URLs
- Primary: http://localhost:5001
- Spare: http://localhost:5002

### Endpoints (sur les deux)
- `GET /health`  
  - 200 → `{"role":"primary|spare","status":"UP"}`
  - 500 → `{"role":"primary|spare","status":"DOWN"}`
- `GET /data`  
  - 200 → JSON avec `role`, `status`, `data`, `ts`
  - 500 → `{"role":"...","error":"Service is DOWN"}`
- `POST /kill` → simule une panne (DOWN)
- `POST /revive` → remet le service UP

### Tests rapides
```bash
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5001/data
curl http://localhost:5002/data

curl -X POST http://localhost:5001/kill
curl -i http://localhost:5001/health
curl -i http://localhost:5001/data

curl -X POST http://localhost:5001/revive
curl http://localhost:5001/health
