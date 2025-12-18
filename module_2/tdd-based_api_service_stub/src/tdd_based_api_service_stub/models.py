from dataclasses import dataclass


@dataclass
class WeatherForecast:
    city: str
    temperature_celsius: int
    condition: str
