import json
import os
from urllib.request import Request, urlopen

DEST = "/Users/harish/FDM_EDA/Docs/taxi_zones.geojson"

SOURCES = [
    "https://raw.githubusercontent.com/toddwschneider/nyc-taxi-data/master/taxi_zones.geojson",
    "https://raw.githubusercontent.com/uber-web/kepler.gl-data/master/nyctrips/data/taxi_zones.geojson",
]


def fetch(url: str):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urlopen(req, timeout=30) as resp:  # type: ignore
        data = resp.read()
    text = data.decode("utf-8-sig", errors="replace").strip()
    if not text or text.startswith("<") or text.startswith("404"):
        return None
    try:
        obj = json.loads(text)
    except Exception:
        return None
    if isinstance(obj, dict) and obj.get("features") and len(obj["features"]) > 200:
        return obj
    return None


def main() -> None:
    for url in SOURCES:
        obj = fetch(url)
        if obj is None:
            continue
        os.makedirs(os.path.dirname(DEST), exist_ok=True)
        with open(DEST, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        print(f"Wrote valid taxi zones GeoJSON to {DEST} with {len(obj['features'])} features")
        return
    raise SystemExit("Failed to fetch a valid taxi zones GeoJSON from known sources.")


if __name__ == "__main__":
    main()


