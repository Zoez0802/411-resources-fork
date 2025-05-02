import logging
import os
import requests

from weather.utils.logger import configure_logger  # Update this path if needed

logger = logging.getLogger(__name__)
configure_logger(logger)


# Load OpenWeatherMap API base URL and API key from environment variables
OPENWEATHERMAP_URL = os.getenv("OPENWEATHERMAP_URL", "https://api.openweathermap.org/data/2.5/weather")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")


def get_current_weather(lat: float, lon: float) -> dict:
    """
    Fetches current weather data for the specified latitude and longitude using OpenWeatherMap.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        dict: Parsed JSON response containing weather data.

    Raises:
        RuntimeError: If the API request fails or response is invalid.
    """
    if not OPENWEATHERMAP_API_KEY:
        raise RuntimeError("Missing OpenWeatherMap API key (OPENWEATHERMAP_API_KEY)")

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric"
    }

    try:
        logger.info(f"Fetching current weather from {OPENWEATHERMAP_URL} for lat={lat}, lon={lon}")
        response = requests.get(OPENWEATHERMAP_URL, params=params, timeout=5)
        response.raise_for_status()

        weather_data = response.json()

        if "main" not in weather_data or "weather" not in weather_data:
            logger.error(f"Incomplete weather data received: {weather_data}")
            raise RuntimeError("Incomplete weather data received.")

        logger.debug(f"Received weather data: {weather_data}")
        logger.info("Successfully fetched current weather.")

        return weather_data

    except requests.exceptions.Timeout:
        logger.error("Request to OpenWeatherMap API timed out.")
        raise RuntimeError("Request to OpenWeatherMap API timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to OpenWeatherMap API failed: {e}")
        raise RuntimeError(f"Request to OpenWeatherMap API failed: {e}")
