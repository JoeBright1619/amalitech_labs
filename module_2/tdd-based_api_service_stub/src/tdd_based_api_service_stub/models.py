from dataclasses import dataclass


@dataclass
class WeatherForecast:
    """
    Represents a weather forecast for a city.

    Attributes:
        city: The name of the city.
        temperature_celsius: The temperature in Celsius.
        condition: The weather condition (e.g., 'Sunny', 'Rainy').
    """

    city: str
    temperature_celsius: int
    condition: str
