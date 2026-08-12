from datetime import date, datetime
from typing import Mapping, Optional


SKIP_TOOL_KEY = "SKIP_TOOL"
SKIP_TOOL_LIMIT_DATE_KEY = "SKIP_TOOL_LIMIT_DATE"
DATE_FORMAT = "%d%m%Y"


def _is_enabled(value: object) -> bool:
    if value is True:
        return True
    return isinstance(value, str) and value.strip().lower() == "true"


def applicable_exclusion(
    exclusions: Mapping[str, Mapping[str, object]], pipeline_name: str
) -> Mapping[str, object]:
    if pipeline_name in exclusions:
        return exclusions[pipeline_name]
    return exclusions.get("All", {})


def should_skip_remote_config(
    exclusion: Mapping[str, object], today: Optional[date] = None
) -> bool:
    if not _is_enabled(exclusion.get(SKIP_TOOL_KEY)):
        return False

    limit_date_value = exclusion.get(SKIP_TOOL_LIMIT_DATE_KEY)
    if not isinstance(limit_date_value, str) or not limit_date_value:
        return False

    try:
        limit_date = datetime.strptime(limit_date_value, DATE_FORMAT).date()
    except ValueError:
        return False

    return (today or date.today()) <= limit_date