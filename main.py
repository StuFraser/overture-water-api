import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from water import check_water, _load_region_data
import os

load_dotenv()

from data_manager import initialise
from water import check_water

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("API_KEY")
logger.info(f"Loaded API key: {API_KEY}")


def verify_api_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initialising water data...")
    initialise()
    _load_region_data()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Overture Water API",
    description="Lightweight water body detection powered by Overture Maps data",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/water/check")
def water_check(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    x_api_key: str = Header(None)
):
    verify_api_key(x_api_key)
    return check_water(lat, lng)