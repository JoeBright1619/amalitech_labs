import pytest
from unittest.mock import patch


@pytest.fixture
def mock_logger():
    with patch("tdd_based_api_service_stub.service.logger") as mocked_logger:
        yield mocked_logger
