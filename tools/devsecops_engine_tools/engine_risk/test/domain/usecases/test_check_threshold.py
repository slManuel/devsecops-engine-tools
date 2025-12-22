from unittest.mock import MagicMock, Mock
from devsecops_engine_tools.engine_risk.src.domain.usecases.check_threshold import (
    CheckThreshold,
)


def create_check_threshold_instance(
    pipeline_name="pipeline_name_test",
    threshold=None,
    risk_exclusions=None,
    vulnerability_management_gateway=None,
    dict_args=None,
    secret_tool=None,
    config_tool=None,
    services=None,
):
    """Helper function to create CheckThreshold instances with default mocks"""
    if threshold is None:
        threshold = {"REMEDIATION_RATE": 1, "SCORE": 1}
    if risk_exclusions is None:
        risk_exclusions = {}
    if vulnerability_management_gateway is None:
        vulnerability_management_gateway = MagicMock()
    if dict_args is None:
        dict_args = {}
    if secret_tool is None:
        secret_tool = MagicMock()
    if config_tool is None:
        config_tool = MagicMock()
    if services is None:
        services = []

    return CheckThreshold(
        pipeline_name,
        threshold,
        risk_exclusions,
        vulnerability_management_gateway,
        dict_args,
        secret_tool,
        config_tool,
        services,
    )


def test_process_pipeline_name():
    """Test when pipeline name is directly in risk_exclusions with THRESHOLD"""
    pipeline_name = "pipeline_name_test"
    threshold = {"REMEDIATION_RATE": 1, "SCORE": 1}
    risk_exclusions = {
        "pipeline_name_test": {
            "THRESHOLD": {"REMEDIATION_RATE": 2, "SCORE": 2}
        }
    }
    expected_threshold = {"REMEDIATION_RATE": 2, "SCORE": 2}

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
    )

    assert check_threshold.process() == expected_threshold


def test_process_pipeline_name_without_threshold_key():
    """Test when pipeline name exists in risk_exclusions but without THRESHOLD key"""
    pipeline_name = "pipeline_name_test"
    threshold = {"REMEDIATION_RATE": 1, "SCORE": 1}
    risk_exclusions = {
        "pipeline_name_test": {
            "OTHER_CONFIG": "value"
        }
    }
    expected_threshold = {"REMEDIATION_RATE": 1, "SCORE": 1}

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
    )

    assert check_threshold.process() == expected_threshold


def test_process_pattern():
    """Test when pipeline name matches a pattern in BY_PATTERN_SEARCH"""
    pipeline_name = "pipeline_name_test"
    threshold = {"REMEDIATION_RATE": 1, "SCORE": 1}
    risk_exclusions = {
        "BY_PATTERN_SEARCH": {
            ".*(pipeline_name).*": {
                "THRESHOLD": {"REMEDIATION_RATE": 2, "SCORE": 2}
            }
        }
    }
    expected_threshold = {"REMEDIATION_RATE": 2, "SCORE": 2}

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
    )

    assert check_threshold.process() == expected_threshold


def test_process_pattern_no_match():
    """Test when pipeline name doesn't match any pattern in BY_PATTERN_SEARCH"""
    pipeline_name = "other_pipeline"
    threshold = {"REMEDIATION_RATE": 1, "SCORE": 1}
    risk_exclusions = {
        "BY_PATTERN_SEARCH": {
            ".*(pipeline_name).*": {
                "THRESHOLD": {"REMEDIATION_RATE": 2, "SCORE": 2}
            }
        }
    }
    expected_threshold = {"REMEDIATION_RATE": 1, "SCORE": 1}

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
    )

    assert check_threshold.process() == expected_threshold


def test_process_default():
    """Test when no exclusions apply, returns default threshold"""
    pipeline_name = "pipeline_name_test"
    threshold = {"REMEDIATION_RATE": 1, "SCORE": 1}
    risk_exclusions = {
        "THRESHOLD": {"REMEDIATION_RATE": 2, "SCORE": 2}
    }
    expected_threshold = {"REMEDIATION_RATE": 1, "SCORE": 1}

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
    )

    assert check_threshold.process() == expected_threshold


def test_process_empty_risk_exclusions():
    """Test with empty risk_exclusions"""
    pipeline_name = "pipeline_name_test"
    threshold = {"REMEDIATION_RATE": 5, "SCORE": 10}
    risk_exclusions = {}
    expected_threshold = {"REMEDIATION_RATE": 5, "SCORE": 10}

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
    )

    assert check_threshold.process() == expected_threshold


def test_process_with_quality_vulnerability_management_no_product_type():
    """Test quality_vulnerability_management when no product type is found"""
    pipeline_name = "pipeline_name_test"
    threshold = {
        "REMEDIATION_RATE": 1,
        "SCORE": 1,
        "QUALITY_VULNERABILITY_MANAGEMENT": {
            "PTS": [{"ProductType1": {"APPS": "ALL", "PROFILE": "STRICT"}}],
            "STRICT": {"REMEDIATION_RATE": 10, "SCORE": 20}
        }
    }
    risk_exclusions = {}

    mock_gateway = MagicMock()
    mock_gateway.get_product_type_pipeline.return_value = None

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
        vulnerability_management_gateway=mock_gateway,
    )

    result = check_threshold.process()
    assert result == threshold


def test_process_with_quality_vulnerability_management_product_type_not_in_config():
    """Test quality_vulnerability_management when product type doesn't match PTS config"""
    pipeline_name = "pipeline_name_test"
    threshold = {
        "REMEDIATION_RATE": 1,
        "SCORE": 1,
        "QUALITY_VULNERABILITY_MANAGEMENT": {
            "PTS": [{"ProductType1": {"APPS": "ALL", "PROFILE": "STRICT"}}],
            "STRICT": {"REMEDIATION_RATE": 10, "SCORE": 20}
        }
    }
    risk_exclusions = {}

    mock_product_type = Mock()
    mock_product_type.name = "ProductType2"

    mock_gateway = MagicMock()
    mock_gateway.get_product_type_pipeline.return_value = mock_product_type

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
        vulnerability_management_gateway=mock_gateway,
    )

    result = check_threshold.process()
    assert result == threshold


def test_process_with_quality_vulnerability_management_app_not_in_list():
    """Test quality_vulnerability_management when service is not in APPS list"""
    pipeline_name = "pipeline_name_test"
    threshold = {
        "REMEDIATION_RATE": 1,
        "SCORE": 1,
        "QUALITY_VULNERABILITY_MANAGEMENT": {
            "PTS": [{"ProductType1": {"APPS": ["service1", "service2"], "PROFILE": "STRICT"}}],
            "STRICT": {"REMEDIATION_RATE": 10, "SCORE": 20}
        }
    }
    risk_exclusions = {}

    mock_product_type = Mock()
    mock_product_type.name = "ProductType1"

    mock_gateway = MagicMock()
    mock_gateway.get_product_type_pipeline.return_value = mock_product_type

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
        vulnerability_management_gateway=mock_gateway,
        services=["service3"],
    )

    result = check_threshold.process()
    assert result == threshold


def test_process_with_quality_vulnerability_management_with_all_apps():
    """Test quality_vulnerability_management with APPS='ALL'"""
    pipeline_name = "pipeline_name_test"
    threshold = {
        "REMEDIATION_RATE": 1,
        "SCORE": 1,
        "QUALITY_VULNERABILITY_MANAGEMENT": {
            "PTS": [{"ProductType1": {"APPS": "ALL", "PROFILE": "STRICT"}}],
            "STRICT": {"REMEDIATION_RATE": 10, "SCORE": 20}
        }
    }
    risk_exclusions = {}

    mock_product_type = Mock()
    mock_product_type.name = "ProductType1"

    mock_gateway = MagicMock()
    mock_gateway.get_product_type_pipeline.return_value = mock_product_type

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
        vulnerability_management_gateway=mock_gateway,
        services=["any_service"],
    )

    result = check_threshold.process()
    assert result == {"REMEDIATION_RATE": 10, "SCORE": 20}


def test_process_with_quality_vulnerability_management_with_specific_app():
    """Test quality_vulnerability_management with specific app in APPS list"""
    pipeline_name = "pipeline_name_test"
    threshold = {
        "REMEDIATION_RATE": 1,
        "SCORE": 1,
        "QUALITY_VULNERABILITY_MANAGEMENT": {
            "PTS": [{"ProductType1": {"APPS": ["service1", "service2"], "PROFILE": "STRICT"}}],
            "STRICT": {"REMEDIATION_RATE": 10, "SCORE": 20}
        }
    }
    risk_exclusions = {}

    mock_product_type = Mock()
    mock_product_type.name = "ProductType1"

    mock_gateway = MagicMock()
    mock_gateway.get_product_type_pipeline.return_value = mock_product_type

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
        vulnerability_management_gateway=mock_gateway,
        services=["service1"],
    )

    result = check_threshold.process()
    assert result == {"REMEDIATION_RATE": 10, "SCORE": 20}


def test_process_with_quality_vulnerability_management_no_profile():
    """Test quality_vulnerability_management when PROFILE key doesn't exist"""
    pipeline_name = "pipeline_name_test"
    threshold = {
        "REMEDIATION_RATE": 1,
        "SCORE": 1,
        "QUALITY_VULNERABILITY_MANAGEMENT": {
            "PTS": [{"ProductType1": {"APPS": "ALL"}}],
            "STRICT": {"REMEDIATION_RATE": 10, "SCORE": 20}
        }
    }
    risk_exclusions = {}

    mock_product_type = Mock()
    mock_product_type.name = "ProductType1"

    mock_gateway = MagicMock()
    mock_gateway.get_product_type_pipeline.return_value = mock_product_type

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
        vulnerability_management_gateway=mock_gateway,
        services=["any_service"],
    )

    result = check_threshold.process()
    assert result == threshold


def test_process_with_quality_vulnerability_management_profile_not_in_config():
    """Test quality_vulnerability_management when PROFILE exists but not in quality config"""
    pipeline_name = "pipeline_name_test"
    threshold = {
        "REMEDIATION_RATE": 1,
        "SCORE": 1,
        "QUALITY_VULNERABILITY_MANAGEMENT": {
            "PTS": [{"ProductType1": {"APPS": "ALL", "PROFILE": "NON_EXISTENT"}}],
            "STRICT": {"REMEDIATION_RATE": 10, "SCORE": 20}
        }
    }
    risk_exclusions = {}

    mock_product_type = Mock()
    mock_product_type.name = "ProductType1"

    mock_gateway = MagicMock()
    mock_gateway.get_product_type_pipeline.return_value = mock_product_type

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
        vulnerability_management_gateway=mock_gateway,
        services=["any_service"],
    )

    result = check_threshold.process()
    assert result == threshold


def test_process_priority_pipeline_name_over_pattern():
    """Test that direct pipeline name has priority over pattern matching"""
    pipeline_name = "pipeline_name_test"
    threshold = {"REMEDIATION_RATE": 1, "SCORE": 1}
    risk_exclusions = {
        "pipeline_name_test": {
            "THRESHOLD": {"REMEDIATION_RATE": 3, "SCORE": 3}
        },
        "BY_PATTERN_SEARCH": {
            ".*(pipeline_name).*": {
                "THRESHOLD": {"REMEDIATION_RATE": 2, "SCORE": 2}
            }
        }
    }
    expected_threshold = {"REMEDIATION_RATE": 3, "SCORE": 3}

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
    )

    assert check_threshold.process() == expected_threshold


def test_process_with_quality_vulnerability_management_multiple_services():
    """Test quality_vulnerability_management with multiple services, one matching"""
    pipeline_name = "pipeline_name_test"
    threshold = {
        "REMEDIATION_RATE": 1,
        "SCORE": 1,
        "QUALITY_VULNERABILITY_MANAGEMENT": {
            "PTS": [{"ProductType1": {"APPS": ["service2"], "PROFILE": "STRICT"}}],
            "STRICT": {"REMEDIATION_RATE": 10, "SCORE": 20}
        }
    }
    risk_exclusions = {}

    mock_product_type = Mock()
    mock_product_type.name = "ProductType1"

    mock_gateway = MagicMock()
    mock_gateway.get_product_type_pipeline.return_value = mock_product_type

    check_threshold = create_check_threshold_instance(
        pipeline_name=pipeline_name,
        threshold=threshold,
        risk_exclusions=risk_exclusions,
        vulnerability_management_gateway=mock_gateway,
        services=["service1", "service2", "service3"],
    )

    result = check_threshold.process()
    assert result == {"REMEDIATION_RATE": 10, "SCORE": 20}
