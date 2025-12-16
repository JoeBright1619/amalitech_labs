import pytest

from src.service import WeatherService
from src.exceptions import CityNotFoundError
from src.provider import WeatherProvider
from src.models import WeatherForecast


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


class MockProvider(WeatherProvider):
    def get_weather(self, city: str) -> WeatherForecast:
        if city == "Kigali":
            return WeatherForecast(
                city="Kigali", temperature_celsius=25, condition="Sunny"
            )
        raise CityNotFoundError(city)


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
