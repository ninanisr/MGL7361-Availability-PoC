# Architecture – MGL7361 Availability PoC

## 1. Overview

This project demonstrates availability tactics using a simple Flask-based microservice architecture composed of:

- Primary Service
- Spare Service
- Load Balancer
- Failure Detection Mechanism (Watchdog)

The objective is to simulate service failure and automatic recovery using redundancy.

---

## 2. System Architecture

The system follows a Primary–Spare redundancy pattern.

### 2.1 Primary Service
- Handles client requests
- Exposes:
  - `/data`
  - `/health`
- Runs on port 5001

### 2.2 Spare Service
- Acts as backup service
- Mirrors Primary endpoints
- Activated when Primary fails
- Runs on port 5002

### 2.3 Load Balancer
- Entry point for all client requests
- Forwards traffic to Primary under normal conditions
- Redirects to Spare upon failure detection
- Runs on port 5000

### 2.4 Failure Detection (Watchdog)
- Periodically checks `/health` endpoint of Primary
- Detects service unavailability
- Triggers failover to Spare

---

## 3. Availability Tactics Applied

### 3.1 Failure Detection
The health check endpoint (`/health`) is used to determine service availability.

### 3.2 Recovery through Redundancy
The Spare service automatically takes over when the Primary service becomes unavailable.

---

## 4. Execution Flow

1. Client → Load Balancer  
2. Load Balancer → Primary  
3. If Primary fails → Load Balancer → Spare  
