import os

import requests


def fetch_current_weather(city: str) -> dict:
    """Fetch current weather data for a given city.

    This function is designed to retrieve real-time weather information.

    Args:
        city (str): The name of the city to get weather data for. Can include country
                   for more precise results (e.g., "London" or "Paris").
    """
    # In a real implementation, you'd call a weather API
    response = requests.get(
        "https://api.weatherapi.com/v1/current.json",
        params={"q": city, "key": os.getenv("WEATHER_API_KEY")},
    )
    return response.json()
