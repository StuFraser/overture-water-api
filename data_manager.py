import os
import json
import logging
import subprocess
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SUPPORTED_REGIONS = os.getenv("SUPPORTED_REGIONS", "NZ").split(",")
DATA_REFRESH_DAYS = int(os.getenv("DATA_REFRESH_DAYS", 30))

# Bounding boxes for each supported region [min_lon, min_lat, max_lon, max_lat]
REGION_BBOX = {
    "NZ": [166.0, -47.5, 178.6, -34.0],
    "AU": [113.0, -43.7, 153.7, 10.7],
    "UK": [-8.2, 49.9, 2.0, 60.9],
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def get_data_path(region: str) -> str:
    return os.path.join(DATA_DIR, f"water_{region.lower()}.geojson")


def data_is_stale(region: str) -> bool:
    path = get_data_path(region)
    if not os.path.exists(path):
        return True
    age_days = (datetime.now(timezone.utc).timestamp() - os.path.getmtime(path)) / 86400
    return age_days > DATA_REFRESH_DAYS


def download_region(region: str):
    bbox = REGION_BBOX.get(region)
    if not bbox:
        logger.error(f"No bounding box configured for region: {region}")
        return

    path = get_data_path(region)
    os.makedirs(DATA_DIR, exist_ok=True)

    logger.info(f"Downloading Overture water data for {region}...")

    cmd = [
        "overturemaps", "download",
        "--bbox", ",".join(map(str, bbox)),
        "-f", "geojson",
        "--type", "water",
        "-o", path
    ]

    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Downloaded water data for {region} → {path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download data for {region}: {e}")


def initialise():
    for region in SUPPORTED_REGIONS:
        region = region.strip().upper()
        if data_is_stale(region):
            download_region(region)
        else:
            logger.info(f"Water data for {region} is current, skipping download")