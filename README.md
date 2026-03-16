# Project Assignment 1 — Containerized Web Application with PostgreSQL

**Stack:** FastAPI (Python) + PostgreSQL + Docker + IPvlan Networking

---

## Project Structure

```
pa1/
├── backend/
│   ├── Dockerfile          # Multi-stage build (builder + runtime)
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .dockerignore
├── database/
│   ├── Dockerfile          # Custom PostgreSQL image
│   └── .dockerignore
├── docker-compose.yml      # Full stack orchestration
└── README.md
```

---

## Prerequisites

- Docker + Docker Compose installed
- WSL2 (Windows) or Linux host
- Network interface: `eth0` with subnet `192.168.160.0/20`

---

## Step 1 — Create IPvlan Network (run once)

```bash
docker network create \
  -d ipvlan \
  --subnet=192.168.160.0/20 \
  --gateway=192.168.160.1 \
  -o ipvlan_mode=l2 \
  -o parent=eth0 \
  ipvlan_net
```

---

## Step 2 — Build and Start

```bash
docker compose up --build -d
```

---

## Step 3 — Test Endpoints

```bash
# Health check
docker exec pa1_backend wget -qO- http://127.0.0.1:8000/health

# POST a record
docker exec pa1_backend wget -qO- \
  --post-data='{"name":"test","value":"hello"}' \
  --header='Content-Type: application/json' \
  http://127.0.0.1:8000/records

# GET all records
docker exec pa1_backend wget -qO- http://127.0.0.1:8000/records
```

---

## Container IPs

| Container     | IP Address       | Port |
|---------------|------------------|------|
| pa1_backend   | 192.168.170.10   | 8000 |
| pa1_db        | 192.168.170.11   | 5432 |

---

## Volume Persistence Test

```bash
# Bring down containers (NOT the volume)
docker compose down

# Confirm volume exists
docker volume ls | grep pgdata

# Restart
docker compose up -d

# Data should still be present
docker exec pa1_backend wget -qO- http://127.0.0.1:8000/records
```

---

## API Endpoints

| Method | Endpoint    | Description         |
|--------|-------------|---------------------|
| GET    | `/health`   | Healthcheck         |
| POST   | `/records`  | Insert a record     |
| GET    | `/records`  | Fetch all records   |

---

## Notes on WSL2 + IPvlan

In WSL2, containers on an ipvlan network cannot be reached directly from the Windows host due to Hyper-V virtual switch NAT isolation. All testing is done from inside the container using `docker exec`. This is a known limitation documented in the project report.
