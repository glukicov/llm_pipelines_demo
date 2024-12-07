from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch

from pipelines.utils import get_date_time_now


def test_get_date_time_now():
    mock_datetime = datetime(69, 4, 20, 6, 6, 6, tzinfo=ZoneInfo("Europe/London"))

    with patch("pipelines.utils.datetime") as mock_datetime_module:
        mock_datetime_module.now.return_value = mock_datetime
        mock_datetime_module.now.tzinfo = ZoneInfo("Europe/London")
        assert get_date_time_now() == "0069-04-20--06-06-06"  # 😏
