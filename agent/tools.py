from langchain_core.tools import tool
import requests

@tool
def get_weather(city: str) -> str:
    """Get weather for a city"""
    # replace with real API
    return f"Weather in {city}: 30°C sunny"