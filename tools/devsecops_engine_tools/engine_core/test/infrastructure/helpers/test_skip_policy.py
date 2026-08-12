from datetime import date

import pytest

from devsecops_engine_tools.engine_core.src.infrastructure.helpers.skip_policy import (
    applicable_exclusion,
    should_skip_remote_config,
)


@pytest.mark.parametrize(
    ("exclusion", "expected"),
    [
        ({"SKIP_TOOL": False, "SKIP_TOOL_LIMIT_DATE": "31122999"}, False),
        ({"SKIP_TOOL": True}, False),
        ({"SKIP_TOOL": True, "SKIP_TOOL_LIMIT_DATE": ""}, False),
        ({"SKIP_TOOL": True, "SKIP_TOOL_LIMIT_DATE": "not-a-date"}, False),
        ({"SKIP_TOOL": True, "SKIP_TOOL_LIMIT_DATE": "01012020"}, False),
        ({"SKIP_TOOL": True, "SKIP_TOOL_LIMIT_DATE": "31122999"}, True),
        ({"SKIP_TOOL": "true", "SKIP_TOOL_LIMIT_DATE": "31122999"}, True),
        ({"SKIP_TOOL": " TRUE ", "SKIP_TOOL_LIMIT_DATE": "31122999"}, True),
        ({"SKIP_TOOL": "false", "SKIP_TOOL_LIMIT_DATE": "31122999"}, False),
        ({"SKIP_TOOL": 1, "SKIP_TOOL_LIMIT_DATE": "31122999"}, False),
    ],
)
def test_should_skip_remote_config(exclusion, expected):
    assert should_skip_remote_config(exclusion, today=date(2026, 8, 12)) is expected


def test_limit_date_includes_current_day():
    exclusion = {"SKIP_TOOL": True, "SKIP_TOOL_LIMIT_DATE": "12082026"}

    assert should_skip_remote_config(exclusion, today=date(2026, 8, 12)) is True


def test_invalid_calendar_date_does_not_skip():
    exclusion = {"SKIP_TOOL": True, "SKIP_TOOL_LIMIT_DATE": "31022026"}

    assert should_skip_remote_config(exclusion, today=date(2026, 8, 12)) is False


def test_applicable_exclusion_prefers_pipeline_over_all():
    exclusions = {
        "All": {"SKIP_TOOL": True},
        "pipeline": {"SKIP_TOOL": False},
    }

    assert applicable_exclusion(exclusions, "pipeline") == exclusions["pipeline"]


def test_applicable_exclusion_falls_back_to_all():
    exclusions = {"All": {"SKIP_TOOL": "true"}}

    assert applicable_exclusion(exclusions, "unknown") == exclusions["All"]