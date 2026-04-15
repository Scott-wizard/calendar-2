from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sqlite3
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

DB_NAME = "calendar.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class Event(BaseModel):
    title: str
    start: str
    end: str | None = None

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/events")
def get_events():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT title, start_time, end_time FROM events")
    rows = cursor.fetchall()
    conn.close()

    events_list = []
    for row in rows:
        events_list.append({
            "title": row[0],
            "start": row[1],
            "end": row[2]
        })
    return events_list

@app.post("/api/events")
def create_event(event: Event):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (title, start_time, end_time) VALUES (?, ?, ?)",
        (event.title, event.start, event.end)
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "message": "Событие сохранено!"}