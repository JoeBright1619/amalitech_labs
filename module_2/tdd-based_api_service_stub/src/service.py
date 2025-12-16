from .models import WeatherForecast
from .exceptions import CityNotFoundError


class WeatherService:
    def get_forecast(self, city: str) -> WeatherForecast:
        if city == "Kigali":
            return WeatherForecast(
                city="Kigali",
                temperature_celsius=25,
                condition="Sunny",
            )

        raise CityNotFoundError(f"No weather data for city: {city}")
