import pytest

from src.service import WeatherService
from src.exceptions import CityNotFoundError


def test_get_forecast_returns_data_for_known_city():
    service = WeatherService()

    result = service.get_forecast("Kigali")

    assert result.city == "Kigali"
    assert result.temperature_celsius == 25
    assert result.condition == "Sunny"


def test_get_forecast_raises_error_for_unknown_city():
    service = WeatherService()

    with pytest.raises(CityNotFoundError):
        service.get_forecast("UnknownCity")
