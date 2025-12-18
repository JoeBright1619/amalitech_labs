from .models import WeatherForecast
from .provider import WeatherProvider
from .logger import logger


class WeatherService:
    def __init__(self, provider: WeatherProvider):
        self.provider = provider

    def get_forecast(self, city: str) -> WeatherForecast:
        logger.info(f"Received request for city: {city}")
        forecast = self.provider.get_weather(city)
        logger.info(f"Returning forecast: {forecast}")
        return self.provider.get_weather(city)
