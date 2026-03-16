from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI(title="PA1 API", version="1.0.0")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "192.168.170.11"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "appdb"),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASSWORD", "apppassword"),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            value TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

class Record(BaseModel):
    name: str
    value: str

@app.post("/records", status_code=201)
def create_record(record: Record):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO records (name, value) VALUES (%s, %s) RETURNING id",
        (record.name, record.value)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": new_id, "name": record.name, "value": record.value}

@app.get("/records")
def get_records():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, value FROM records")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "name": r[1], "value": r[2]} for r in rows]

@app.get("/health")
def health():
    try:
        conn = get_conn()
        conn.close()
        return {"status": "healthy", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
