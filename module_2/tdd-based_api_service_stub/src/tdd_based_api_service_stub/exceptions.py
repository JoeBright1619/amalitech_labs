class WeatherServiceError(Exception):
    """Base exception for weather service errors."""


class CityNotFoundError(WeatherServiceError):
    """Raised when a city is not found."""
