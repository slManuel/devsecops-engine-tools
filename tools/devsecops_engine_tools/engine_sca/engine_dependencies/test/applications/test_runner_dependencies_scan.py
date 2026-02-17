from devsecops_engine_tools.engine_sca.engine_dependencies.src.applications.runner_dependencies_scan import (
    runner_engine_dependencies,
)

from unittest.mock import patch


def test_init_engine_dependencies_xray():
    """Test that runner_engine_dependencies properly initializes with XRAY tool"""
    with patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.applications.runner_dependencies_scan.init_engine_dependencies"
    ) as mock_init_engine_dependencies, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.applications.runner_dependencies_scan.XrayScan"
    ) as mock_xray, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.applications.runner_dependencies_scan.XrayDeserializator"
    ) as mock_xray_deser:
        # Mock the return value to match what init_engine_dependencies returns (3 values)
        mock_findings = ["finding1", "finding2"]
        mock_input_core = {"key": "value"}
        mock_sbom = ["component1"]
        mock_init_engine_dependencies.return_value = (mock_findings, mock_input_core, mock_sbom)
        
        dict_args = {"remote_config_repo": "remote_repo", "remote_config_branch": ""}
        token = "token"
        config_tool = {
            "ENGINE_DEPENDENCIES": {"ENABLED": "true", "TOOL": "XRAY"},
        }

        findings_list, input_core, sbom_components, tool_run = runner_engine_dependencies(dict_args, config_tool, token, None, None, None)

        # Verify init_engine_dependencies was called
        mock_init_engine_dependencies.assert_called_once()
        
        # Verify return values
        assert findings_list == mock_findings
        assert input_core == mock_input_core
        assert sbom_components == mock_sbom
        assert tool_run is not None  # tool_run should be the XrayScan instance


def test_init_engine_dependencies_dependency_check():
    """Test that runner_engine_dependencies properly initializes with DEPENDENCY_CHECK tool"""
    with patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.applications.runner_dependencies_scan.init_engine_dependencies"
    ) as mock_init_engine_dependencies, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.applications.runner_dependencies_scan.DependencyCheckTool"
    ) as mock_dep_check, patch(
        "devsecops_engine_tools.engine_sca.engine_dependencies.src.applications.runner_dependencies_scan.DependencyCheckDeserialize"
    ) as mock_dep_check_deser:
        # Mock the return value to match what init_engine_dependencies returns (3 values)
        mock_findings = ["finding1", "finding2"]
        mock_input_core = {"key": "value"}
        mock_sbom = ["component1"]
        mock_init_engine_dependencies.return_value = (mock_findings, mock_input_core, mock_sbom)
        
        dict_args = {"remote_config_repo": "remote_repo", "remote_config_branch": ""}
        token = "token"
        config_tool = {
            "ENGINE_DEPENDENCIES": {"ENABLED": "true", "TOOL": "DEPENDENCY_CHECK"},
        }

        findings_list, input_core, sbom_components, tool_run = runner_engine_dependencies(dict_args, config_tool, token, None, None, None)

        # Verify init_engine_dependencies was called
        mock_init_engine_dependencies.assert_called_once()
        
        # Verify return values
        assert findings_list == mock_findings
        assert input_core == mock_input_core
        assert sbom_components == mock_sbom
        assert tool_run is not None  # tool_run should be the DependencyCheckTool instance
