import os
from dotenv import load_dotenv

# load_dotenv() reads the .env file and puts each
# line into os.environ so os.getenv() can find them.
load_dotenv()


# ── The 5 UK cities we want weather data for ────
# Open-Meteo needs latitude and longitude, not city names.
# Geographic spread: England, Scotland, Wales, Northern Ireland.
CITIES = [
    {"name": "London",     "latitude": 51.5085, "longitude": -0.1257},
    {"name": "Manchester", "latitude": 53.4808, "longitude": -2.2426},
    {"name": "Edinburgh",  "latitude": 55.9533, "longitude": -3.1883},
    {"name": "Cardiff",    "latitude": 51.4837, "longitude": -3.1681},
    {"name": "Belfast",    "latitude": 54.5973, "longitude": -5.9301},
]


# ── Open-Meteo API settings ───
# Base URL for the forecast endpoint (no API key required).
API_BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Weather variables to request from the API.
# These map to columns in the database table.
# "daily" prefix means one value per day (not per hour).
API_DAILY_VARIABLES = [
    "temperature_2m_max",       # Maximum air temperature at 2m height (°C)
    "temperature_2m_min",       # Minimum air temperature at 2m height (°C)
    "precipitation_sum",        # Total rainfall/snowfall for the day (mm)
    "windspeed_10m_max",        # Maximum wind speed at 10m height (km/h)
    "weathercode",              # WMO weather interpretation code (0=clear, 95=storm etc.)
]

# The timezone Open-Meteo should use when returning daily values.
API_TIMEZONE = "Europe/London"

# Number of days ahead to fetch forecasts for (0 = today only, 6 = one week).
API_FORECAST_DAYS = 7


# ── PostgreSQL database settings ───
# Credentials are loaded from the .env file — never hardcoded here.
# os.getenv() returns None if a variable is missing, so we supply defaults
# only for non-sensitive values like host and port.
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "weather_db"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# Name of the table we will create/insert into in PostgreSQL.
DB_TABLE_NAME = "uk_weather_daily"


# ── Reports settings ───
# Directory (relative to project root) where chart images will be saved.
REPORTS_OUTPUT_DIR = "reports/output"