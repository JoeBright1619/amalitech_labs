from abc import ABC, abstractmethod
from .models import WeatherForecast
from .exceptions import CityNotFoundError  # noqa: F401


class WeatherProvider(ABC):
    """Abstract interface for weather data sources."""

    @abstractmethod
    def get_weather(self, city: str) -> WeatherForecast:
        """Return WeatherForecast for a city or raise CityNotFoundError."""
        raise NotImplementedError
