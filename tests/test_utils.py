from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch

from pipelines.utils import get_date_time_now


def test_get_date_time_now():
    mock_datetime = datetime(2024, 8, 8, 15, 27, 51, tzinfo=ZoneInfo("Europe/London"))

    with patch("pipelines.utils.datetime") as mock_datetime_module:
        mock_datetime_module.now.return_value = mock_datetime
        mock_datetime_module.now.tzinfo = ZoneInfo("Europe/London")
        assert get_date_time_now() == "2024-08-08--15-27-51"
