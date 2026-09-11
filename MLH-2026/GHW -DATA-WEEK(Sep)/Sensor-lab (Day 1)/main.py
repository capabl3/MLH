import os
import random
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import timescaledb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, select
from timescaledb import TimescaleModel

load_dotenv()
engine = timescaledb.create_engine(os.environ["DATABASE_URL"])

class MachineReading(TimescaleModel, table=True):
    machine_id: int = Field(index=True)
    vibration: float
    power: float


class ReadingIn(BaseModel):
    machine_id: int
    vibration: float
    power: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    timescaledb.metadata.create_all(engine)
    yield


app = FastAPI(title="Sensor Lab", lifespan=lifespan)


@app.post("/readings")
def add_reading(data: ReadingIn):
    reading = MachineReading(**data.model_dump())
    with Session(engine) as session:
        session.add(reading)
        session.commit()
        session.refresh(reading)
    return reading

@app.get("/readings")
def list_readings(machine_id: int = 2, limit: int = 20):
    with Session(engine) as session:
        return session.exec(
            select(MachineReading)
            .where(MachineReading.machine_id == machine_id)
            .order_by(MachineReading.time.desc())
            .limit(limit)
        ).all()

@app.get("/readings/trend")
def trend(machine_id: int = 2, interval: str = "1 hour"):
    with Session(engine) as session:
        return timescaledb.time_bucket_query(
            session,
            MachineReading,
            interval=interval,
            metric_field="vibration",
            filters=[MachineReading.machine_id == machine_id],
        )

@app.post("/seed")
def seed(machine_id: int = 2, count: int = 500):
    week = 7 * 24 * 60 * 60
    now = datetime.now(timezone.utc)
    rows = [
        MachineReading(
            machine_id=machine_id,
            time=now - timedelta(seconds=random.randint(0, week)),
            vibration=round(random.uniform(1.0, 5.5), 3),
            power=round(random.uniform(3.0, 4.5), 3),
        )
        for _ in range(count)
    ]
    with Session(engine) as session:
        session.add_all(rows)
        session.commit()
    return {"inserted": len(rows), "machine_id": machine_id}

PAGE = """<!doctype html>
<title>Sensor Lab</title>
<style>
  body { font: 15px system-ui, sans-serif; margin: 40px auto; max-width: 900px; color: #22352c; }
  button { font: inherit; padding: 9px 16px; border: 1px solid #d96a37; background: #d96a37;
           color: white; border-radius: 5px; cursor: pointer; }
  svg { width: 100%; height: 320px; border: 1px solid #dddfd5; border-radius: 6px; }
  #out { font: 13px ui-monospace, monospace; color: #788078; }
</style>
<h1>Sensor Lab</h1>
<p><button onclick="seed()">Add 500 random readings</button> <span id="out"></span></p>
<svg id="chart" viewBox="0 0 600 200" preserveAspectRatio="none"></svg>
<script>
async function seed() {
  out.textContent = "seeding...";
  const r = await fetch("/seed", { method: "POST" });
  const d = await r.json();
  out.textContent = `inserted ${d.inserted}`;
  draw();
}
async function draw() {
  const rows = await (await fetch("/readings/trend")).json();
  if (!rows.length) { out.textContent = "no data yet"; return; }
  const pts = rows.slice().reverse().map(r => r.avg);
  const lo = Math.min(...pts), hi = Math.max(...pts);
  const d = pts.map((v, i) =>
    `${(i / Math.max(1, pts.length - 1)) * 600},${190 - ((v - lo) / (hi - lo || 1)) * 180}`).join(" ");
  chart.innerHTML = `<polyline points="${d}" fill="none" stroke="#d96a37" stroke-width="2"
    vector-effect="non-scaling-stroke"/>`;
}
draw();
</script>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE