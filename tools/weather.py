import os
from typing import Dict

import requests


def fetch_current_weather(city: str) -> Dict[str, any]:
    """Fetch current weather data for a given city.

    This function is designed to retrieve real-time weather information.

    Args:
        city (str): The name of the city to get weather data for. Can include country
                   for more precise results (e.g., "London" or "Paris").
                   
    Returns:
        Dict[str, any]: Weather data or error information
    """
    if not city or not city.strip():
        return {"error": "City name cannot be empty"}
    
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return {"error": "Weather API key not configured"}
    
    try:
        response = requests.get(
            "https://api.weatherapi.com/v1/current.json",
            params={"q": city.strip(), "key": api_key},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Weather API request timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Weather API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error fetching weather: {str(e)}"}
