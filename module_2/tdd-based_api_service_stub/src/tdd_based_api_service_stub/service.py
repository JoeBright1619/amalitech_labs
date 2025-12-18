from .models import WeatherForecast
from .provider import WeatherProvider
from .logger import logger


class WeatherService:
    """
    Service for retrieving weather forecasts.

    This service acts as a high-level API, delegating the actual
    data fetching to a WeatherProvider implementation.
    """

    def __init__(self, provider: WeatherProvider):
        """Initialize the service with a weather provider."""
        self.provider = provider

    def get_forecast(self, city: str) -> WeatherForecast:
        """
        Get the weather forecast for a specific city.

        Args:
            city: The name of the city.

        Returns:
            A WeatherForecast object.

        Raises:
            CityNotFoundError: If the city is not recognized by the provider.
        """
        logger.info(f"Received request for city: {city}")
        forecast = self.provider.get_weather(city)
        logger.info(f"Returning forecast: {forecast}")
        return self.provider.get_weather(city)
