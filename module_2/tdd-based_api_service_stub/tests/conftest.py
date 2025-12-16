import pytest
from unittest.mock import patch


@pytest.fixture
def mock_logger():
    with patch("src.service.logger") as mocked_logger:
        yield mocked_logger
