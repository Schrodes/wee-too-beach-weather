#!/usr/bin/env python3
"""Publish only approved outdoor ThingSpeak fields. Never publish credentials."""
import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from zoneinfo import ZoneInfo

CHANNEL_ID = "2878327"
KEY = os.environ["THINGSPEAK_READ_API_KEY"].strip()
if not KEY:
    raise RuntimeError("Empty ThingSpeak read API key")
OUTPUT = Path("data")
OUTPUT.mkdir(exist_ok=True)
PUBLIC_FIELDS = (2, 3, 4, 5, 6, 8)
HISTORY_FIELDS = (2, 3, 4, 5)

def get_feeds(params):
    query = urlencode({"api_key": KEY, **params})
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?{query}"
    with urlopen(url, timeout=45) as response:
        payload = json.load(response)
    if "feeds" not in payload:
        raise RuntimeError("ThingSpeak returned no feeds array")
    return payload["feeds"]

def save(name, obj):
    (OUTPUT / name).write_text(json.dumps(obj, separators=(",", ":")), encoding="utf-8")

def numeric(raw):
    if raw is None or str(raw).strip() == "":
        return None
    try:
        number = float(raw)
        return number if math.isfinite(number) else None
    except (ValueError, TypeError):
        return None

recent = get_feeds({"results": 100})
values = {f"field{i}": None for i in PUBLIC_FIELDS}
times = {f"field{i}": None for i in PUBLIC_FIELDS}
for feed in reversed(recent):
    for i in PUBLIC_FIELDS:
        field = f"field{i}"
        value = numeric(feed.get(field))
        if values[field] is None and value is not None:
            values[field] = value
            times[field] = feed.get("created_at")
values["field_updated_at"] = times
values["created_at"] = recent[-1].get("created_at") if recent else None
save("weather.json", values)

now = datetime.now(timezone.utc)
midnight_local = now.astimezone(ZoneInfo("America/Regina")).replace(hour=0, minute=0, second=0, microsecond=0)
today_start = midnight_local.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
today_feeds = get_feeds({"start": today_start, "results": 8000})
temps = [v for f in today_feeds if (v := numeric(f.get("field2"))) is not None]
save("today.json", {"high": max(temps) if temps else None, "low": min(temps) if temps else None,
                    "count": len(temps), "limit_reached": len(today_feeds) >= 8000})

for days in (1, 7, 30):
    start = (now - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    feeds = get_feeds({"start": start, "results": 8000})
    cleaned = []
    for feed in feeds:
        point = {"created_at": feed.get("created_at")}
        for i in HISTORY_FIELDS:
            point[f"field{i}"] = numeric(feed.get(f"field{i}"))
        cleaned.append(point)
    save(f"history_{days}.json", {"feeds": cleaned, "days": days, "limit_reached": len(feeds) >= 8000})
print("Published outdoor fields only: 2, 3, 4, 5, 6, 8; history fields 2, 3, 4, 5")
