import requests
from logger import get_logger
from config.settings import (
    API_BASE_URL, API_DAILY_VARIABLES,
    API_FORECAST_DAYS, API_TIMEZONE, CITIES,
)


logger = get_logger(__name__)


def fetch_city_weather(city):
    """Fetch one week of forecast data for a single city from the weather API.

    Args:
        city (dict): A dictionary containing 'name', 'latitude', and 'longitude'.

    Returns:
        dict | None: The raw JSON response from the API if successful; 
            None if the HTTP request fails or times out.
    """

    # Build the query parameters from our settings file
    params = {
        "latitude":      city["latitude"],
        "longitude":     city["longitude"],
        "daily":         ",".join(API_DAILY_VARIABLES),
        "timezone":      API_TIMEZONE,
        "forecast_days": API_FORECAST_DAYS,
    }

    logger.info("Fetching data for %s...", city["name"])

    try:
        # Make the HTTP GET request. timeout=10 prevents
        # the script hanging forever on a slow connection.
        response = requests.get(API_BASE_URL, params=params, timeout=10)

        # Raises an error for bad responses (404, 500 etc.)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error("Failed for %s: %s", city["name"], e)
        return None
    

def extract_all_cities():
    """Fetch weather data for all configured cities, skipping failed requests.

    Iterates through `CITIES`, requests data from `fetch_city_weather()`, and
    injects the city's name into the successful raw responses.

    Returns:
        list[dict]: A list of raw API payloads, each including a 'city_name' key.
    """
    results = []

    for city in CITIES:
        raw_data = fetch_city_weather(city)
        if raw_data is not None:
            raw_data["city_name"] = city["name"]
            results.append(raw_data)

    logger.info("Fetched %d cities successfully.", len(results))
    return results


if __name__ == "__main__":
    
    city_data = extract_all_cities()
    for record in city_data:
        print(f"\n{record['city_name']}:")
        print(f"  Dates:     {record['daily']['time']}")
        print(f"  Max temps: {record['daily']['temperature_2m_max']}")
