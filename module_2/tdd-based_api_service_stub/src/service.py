from .models import WeatherForecast
from .provider import WeatherProvider


class WeatherService:
    def __init__(self, provider: WeatherProvider):
        self.provider = provider

    def get_forecast(self, city: str) -> WeatherForecast:
        return self.provider.get_weather(city)
