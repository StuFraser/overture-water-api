# 💧 overture-water-api

> A lightweight, self-contained REST API for water body detection and classification — powered by Overture Maps data.

Drop a coordinate anywhere in a supported region and instantly know whether it falls within a natural water body, what type it is, whether it's fresh or salt water, and what it's called. No third-party API calls at runtime. No billing surprises.

---

## ✨ Features

- **Point-in-water detection** — Is a given lat/lng coordinate within a water body?
- **Water type classification** — Ocean, lake, river, reservoir, estuary, harbour, and more
- **Fresh vs. salt water** — Explicit `is_salt` flag on every response
- **Named water bodies** — Returns the name of the water body where available
- **Regional data bundles** — Download and cache Overture water data per region on startup
- **Auto-refresh** — Configurable data freshness checks keep regional data current
- **Simple API key auth** — Lightweight static key protection, no user management needed
- **Zero runtime dependencies** — All queries run against a local GeoParquet/GeoJSON file

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
git clone https://github.com/StuFraser/overture-water-api.git
cd overture-water-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Copy the example env file and configure it:

```bash
cp .env.example .env
```

```env
API_KEY=your-random-secret-key-here
SUPPORTED_REGIONS=NZ
DATA_REFRESH_DAYS=30
```

### Run

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

On first startup, the service will automatically download Overture water data for each configured region. This may take a moment — subsequent startups will use the cached local data.

---

## 📡 API Reference

### `GET /water/check`

Check whether a coordinate falls within a water body.

**Headers**

| Header | Required | Description |
|--------|----------|-------------|
| `X-API-Key` | ✅ | Your configured API key |

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | ✅ | Latitude |
| `lng` | float | ✅ | Longitude |

**Example Request**

```bash
curl -X GET "http://localhost:8000/water/check?lat=-36.8485&lng=174.7633" \
  -H "X-API-Key: your-secret-key"
```

**Example Response — Water detected**

```json
{
  "is_water": true,
  "name": "Waitemata Harbour",
  "subtype": "water",
  "class": "harbour",
  "is_salt": true,
  "is_intermittent": false,
  "confidence": "high"
}
```

**Example Response — No water**

```json
{
  "is_water": false,
  "name": null,
  "subtype": null,
  "class": null,
  "is_salt": null,
  "is_intermittent": null,
  "confidence": "high"
}
```

### `GET /health`

Service health check. Returns current status and data freshness per region.

```json
{
  "status": "ok",
  "regions": {
    "NZ": {
      "loaded": true,
      "last_updated": "2026-02-01T00:00:00Z",
      "age_days": 29
    }
  }
}
```

---

## 🗺️ Supported Regions

Regions are configured via the `SUPPORTED_REGIONS` environment variable as a comma-separated list.

| Code | Region |
|------|--------|
| `NZ` | New Zealand |
| `AU` | Australia |
| `UK` | United Kingdom |

Adding a new region is as simple as adding its code to the config — the service handles the rest on next startup.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Query Engine | DuckDB |
| Data Download | overturemaps CLI |
| Geospatial | Shapely / GeoPandas |
| Config | python-dotenv |

---

## 🏗️ Project Structure

```
overture-water-api/
├── main.py              # FastAPI app & routes
├── data/                # Local regional GeoJSON data files
│   └── water_nz.geojson
├── services/
│   ├── water.py         # Point-in-water query logic
│   └── data_manager.py  # Overture data download & refresh
├── middleware/
│   └── auth.py          # API key validation
├── .env.example
├── requirements.txt
└── Dockerfile
```

---

## 🐳 Docker

```bash
docker build -t overture-water-api .
docker run -p 8000:8000 --env-file .env overture-water-api
```

---

## 📦 Used By

- [AquaRipple](https://github.com/StuFraser/aqua-ripple) — Community water quality monitoring platform

---

## 📄 Data Attribution & Licensing

This service uses geospatial data from the **Overture Maps Foundation**.

### Overture Maps — Base/Water Theme

The water feature data used by this service is sourced from the Overture Maps Foundation `base` theme and is distributed under the **Open Database License (ODbL) v1.0**, as it incorporates data derived from OpenStreetMap.

**Required attribution:**

> © OpenStreetMap contributors, Overture Maps Foundation

Under the ODbL:
- You are free to use, modify, and distribute the data
- Any derivative databases must also be licensed under ODbL
- Attribution to both OpenStreetMap contributors and Overture Maps Foundation is required

### OpenStreetMap

Portions of the underlying data are © **OpenStreetMap contributors**, licensed under the [Open Database License (ODbL) v1.0](https://opendatacommons.org/licenses/odbl/1-0/).

### Full License Texts

- [ODbL v1.0](https://opendatacommons.org/licenses/odbl/1-0/)
- [CDLA Permissive v2.0](https://cdla.dev/permissive-2-0/)
- [Overture Maps Attribution Requirements](https://docs.overturemaps.org/attribution/)

---

## 📝 License

This project's source code is licensed under the [MIT License](LICENSE).

Data used at runtime carries its own licensing terms as described in the Data Attribution section above.

---

## 🙏 Acknowledgements

- [Overture Maps Foundation](https://overturemaps.org) — Open map data
- [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) — Underlying community map data
- [DuckDB](https://duckdb.org) — Blazing fast local analytics
