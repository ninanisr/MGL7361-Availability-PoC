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
