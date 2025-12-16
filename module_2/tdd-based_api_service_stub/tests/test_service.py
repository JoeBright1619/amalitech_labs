import pytest

from src.service import WeatherService
from src.exceptions import CityNotFoundError
from src.provider import WeatherProvider
from src.models import WeatherForecast


class MockProvider(WeatherProvider):
    def get_weather(self, city: str) -> WeatherForecast:
        known_cities = {
            "Kigali": WeatherForecast(
                city="Kigali", temperature_celsius=25, condition="Sunny"
            ),
            "Musanze": WeatherForecast(
                city="Musanze", temperature_celsius=22, condition="Cloudy"
            ),
            "Huye": WeatherForecast(
                city="Huye", temperature_celsius=23, condition="Rainy"
            ),
        }
        if city in known_cities:
            return known_cities[city]
        raise CityNotFoundError(city)


def test_get_forecast_returns_data_for_known_city():
    provider = MockProvider()
    service = WeatherService(provider)

    result = service.get_forecast("Kigali")

    assert result.city == "Kigali"
    assert result.temperature_celsius == 25
    assert result.condition == "Sunny"


def test_get_forecast_raises_error_for_unknown_city():
    provider = MockProvider()
    service = WeatherService(provider)

    with pytest.raises(CityNotFoundError):
        service.get_forecast("UnknownCity")


def test_service_uses_provider():
    provider = MockProvider()
    service = WeatherService(provider=provider)

    result = service.get_forecast("Kigali")
    assert result.city == "Kigali"

    with pytest.raises(CityNotFoundError):
        service.get_forecast("UnknownCity")


def test_get_forecast_logs(mock_logger):
    provider = MockProvider()
    service = WeatherService(provider=provider)

    service.get_forecast("Kigali")

    # Assert that logger.info was called at least twice
    assert mock_logger.info.call_count >= 2


# Parametrized test for known cities
@pytest.mark.parametrize(
    "city,expected_temp,expected_condition",
    [
        ("Kigali", 25, "Sunny"),
        ("Musanze", 22, "Cloudy"),
        ("Huye", 23, "Rainy"),
    ],
)
def test_get_forecast_known_cities(city, expected_temp, expected_condition):
    provider = MockProvider()
    service = WeatherService(provider=provider)

    forecast = service.get_forecast(city)

    assert forecast.city == city
    assert forecast.temperature_celsius == expected_temp
    assert forecast.condition == expected_condition


# Parametrized test for unknown cities
@pytest.mark.parametrize("city", ["UnknownCity", "Nyiragongo", ""])
def test_get_forecast_unknown_cities(city):
    provider = MockProvider()
    service = WeatherService(provider=provider)

    with pytest.raises(CityNotFoundError):
        service.get_forecast(city)
