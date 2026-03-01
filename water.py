import os
import logging
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from data_manager import get_data_path, SUPPORTED_REGIONS, REGION_BBOX

logger = logging.getLogger(__name__)

# Cache loaded GeoDataFrames in memory — no need to reload on every request
_region_data: dict = {}


def _clean(value):
    if value is None:
        return None
    try:
        if np.isnan(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _load_region_data():
    for region in SUPPORTED_REGIONS:
        region = region.strip().upper()
        path = get_data_path(region)
        if os.path.exists(path):
            logger.info(f"Loading {region} water data into memory...")
            _region_data[region] = gpd.read_file(path)
        else:
            logger.warning(f"No data file found for {region} — was initialise() called?")


def _get_region_for_point(lat: float, lng: float) -> str | None:
    for region, bbox in REGION_BBOX.items():
        min_lon, min_lat, max_lon, max_lat = bbox
        if min_lon <= lng <= max_lon and min_lat <= lat <= max_lat:
            return region
    return None


def check_water(lat: float, lng: float) -> dict:
    region = _get_region_for_point(lat, lng)

    if not region:
        return {
            "is_water": False,
            "name": None,
            "subtype": None,
            "class": None,
            "is_salt": None,
            "is_intermittent": None,
            "confidence": "low",
            "reason": "Coordinate outside all supported regions"
        }

    if region not in _region_data:
        _load_region_data()

    if region not in _region_data:
        return {
            "is_water": False,
            "name": None,
            "subtype": None,
            "class": None,
            "is_salt": None,
            "is_intermittent": None,
            "confidence": "low",
            "reason": "Regional data unavailable"
        }

    gdf = _region_data[region]
    point = Point(lng, lat)  # Shapely is lon/lat order
    matches = gdf[gdf.geometry.contains(point)]

    if matches.empty:
        return {
            "is_water": False,
            "name": None,
            "subtype": None,
            "class": None,
            "is_salt": None,
            "is_intermittent": None,
            "confidence": "high"
        }

    match = matches.iloc[0]

    return {
        "is_water": True,
        "name": match.get("names", {}).get("primary") if isinstance(match.get("names"), dict) else None,
        "subtype": _clean(match.get("subtype")),
        "class": _clean(match.get("class")),
        "is_salt": _clean(match.get("is_salt")),
        "is_intermittent": _clean(match.get("is_intermittent")),
        "confidence": "high"
    }