"""24/7 Phone Support Agent - webhook service.

ElevenLabs agents call GET /screenings?city=... as a webhook tool during a
conversation. The response includes a short `summary` written to be read
aloud, plus the structured results.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query

load_dotenv()

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "screenings.json"

app = FastAPI(title="24/7 Phone Support Agent")


def load_screenings() -> list[dict]:
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def check_secret(x_api_key: str | None) -> None:
    """Reject requests without the shared secret, if one is configured."""
    secret = os.getenv("WEBHOOK_SECRET")
    if secret and x_api_key != secret:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def spoken_time(iso: str) -> str:
    """'2026-12-04T19:30' -> 'Friday, December 4 at 7:30 PM'."""
    dt = datetime.fromisoformat(iso)
    hour = dt.strftime("%I").lstrip("0")
    return f"{dt.strftime('%A, %B')} {dt.day} at {hour}:{dt.strftime('%M %p')}"


def build_summary(city: str, matches: list[dict]) -> str:
    if not matches:
        return f"I couldn't find any upcoming screenings in {city}."
    parts = [f"{m['film']} at {m['venue']} on {spoken_time(m['starts_at'])}" for m in matches]
    noun = "screening" if len(matches) == 1 else "screenings"
    return f"There {'is' if len(matches) == 1 else 'are'} {len(matches)} {noun} in {city}: " + "; ".join(parts) + "."


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/screenings")
def screenings(
    city: str = Query(..., min_length=1, description="City the caller is asking about"),
    x_api_key: str | None = Header(default=None),
) -> dict:
    check_secret(x_api_key)
    wanted = city.strip().lower()
    matches = sorted(
        (s for s in load_screenings() if s["city"].lower() == wanted),
        key=lambda s: s["starts_at"],
    )
    return {
        "city": city.strip(),
        "count": len(matches),
        "summary": build_summary(city.strip(), matches),
        "screenings": matches,
    }
