"""Weather tool for fetching current weather data"""

from typing import Dict, Any
import requests

from .base_tool import BaseTool
from ..config import settings


class WeatherTool(BaseTool):
    """Tool for fetching current weather information"""
    
    def name(self) -> str:
        return "weather"
    
    def execute(self, city: str) -> Dict[str, Any]:
        """Fetch current weather data for a given city"""
        return fetch_current_weather(city)
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_current_weather",
                "description": "Fetch current weather data for a given city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city to get weather data for"
                        }
                    },
                    "required": ["city"]
                }
            }
        }


def fetch_current_weather(city: str) -> Dict[str, Any]:
    """Fetch current weather data for a given city.

    This function is designed to retrieve real-time weather information.

    Args:
        city (str): The name of the city to get weather data for. Can include country
                   for more precise results (e.g., "London" or "Paris").
                   
    Returns:
        Dict[str, Any]: Weather data or error information
    """
    if not city or not city.strip():
        return {"error": "City name cannot be empty"}
    
    api_key = settings.weather_api_key
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


# For backward compatibility, export the function
__all__ = ["WeatherTool", "fetch_current_weather"]