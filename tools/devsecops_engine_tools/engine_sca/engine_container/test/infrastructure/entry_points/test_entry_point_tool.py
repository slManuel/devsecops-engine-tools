from devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool import (
    init_engine_sca_rm,
)
from unittest.mock import patch, Mock

remote_config = {
    "PRISMA_CLOUD": {
        "TWISTCLI_PATH": "twistcli",
        "PRISMA_CONSOLE_URL": "",
        "PRISMA_API_VERSION":"",
        "SBOM_FORMAT": "cyclonedx_json"
    },
    "TRIVY": {
        "TRIVY_VERSION": "0.51.4",
        "SBOM_FORMAT": "cyclonedx"
    },
    "SBOM": {
        "ENABLED": False,
        "BRANCH_FILTER": [
            "trunk",
            "main"
        ]
    },
    "GET_IMAGE_BASE": False,
    "VALIDATE_BASE_IMAGE_DATE": {
        "ENABLED": False,
        "REFERENCE_IMAGE_DATE": "20250206"
    },
    "MESSAGE_INFO_ENGINE_CONTAINER": "message custom",
    "IGNORE_SEARCH_PATTERN":"(.*_demo0|.*_cer)",
    "REGEX_CLEAN_END_PIPELINE_NAME": "",
    "THRESHOLD": {
        "VULNERABILITY": {
            "Critical": 4,
            "High": 10,
            "Medium": 20,
            "Low": 999
        },
        "COMPLIANCE": {
            "Critical": 1
        }
    }
}


def test_init_engine_sca_rm():
    with patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.ContainerScaScan"
    ) as mock_container_sca_scan, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.SetInputCore"
    ) as mock_set_input_core, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.HandleRemoteConfigPatterns"
    ) as mock_handle_remote_config_patterns, patch(
        "devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway"
    ) as mock_devops_platform_gateway:
        dict_args = {"remote_config_repo": "remote_repo", "image_to_scan":"image", "remote_config_branch": ""}
        token = "token"
        tool = "tool"
        mock_handle_remote_config_patterns.process_handle_working_directory.return_value = (
            "working_dir"
        )
        mock_handle_remote_config_patterns.process_handle_skip_tool.return_value = False
        mock_handle_remote_config_patterns.process_handle_analysis_pattern.return_value = (
            True
        )
        mock_container_sca_scan.process.return_value = ("scan_result.json", None)

        mock_devops_platform_gateway.get_remote_config.return_value = remote_config

        deserialized, core_input, sbom_components = init_engine_sca_rm(
            Mock(),
            mock_devops_platform_gateway,
            Mock(),
            Mock(),
            Mock(),
            dict_args,
            token,
            tool,
        )


def test_init_engine_sca_rm_skip_tool():
    with patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.ContainerScaScan"
    ) as mock_container_sca_scan, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.SetInputCore"
    ) as mock_set_input_core, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.HandleRemoteConfigPatterns"
    ) as mock_handle_remote_config_patterns, patch(
        "devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway"
    ) as mock_devops_platform_gateway:
        dict_args = {"remote_config_repo": "remote_repo", "image_to_scan":"image", "remote_config_branch": ""}
        token = "token"
        tool = "tool"
        mock_handle_remote_config_patterns.process_handle_working_directory.return_value = (
            "working_dir"
        )
        mock_handle_remote_config_patterns.process_handle_skip_tool.return_value = True
        mock_handle_remote_config_patterns.process_handle_analysis_pattern.return_value = (
            True
        )

        mock_devops_platform_gateway.get_remote_config.return_value = remote_config

        deserialized, core_input, sbom_components = init_engine_sca_rm(
            Mock(),
            mock_devops_platform_gateway,
            Mock(),
            Mock(),
            Mock(),
            dict_args,
            token,
            tool,
        )
        assert deserialized == []
        mock_container_sca_scan.assert_not_called()


def test_init_engine_sca_rm_no_exclusions():
    with patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.ContainerScaScan"
    ) as mock_container_sca_scan, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.SetInputCore"
    ) as mock_set_input_core, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.HandleRemoteConfigPatterns"
    ) as mock_handle_remote_config_patterns, patch(
        "devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway"
    ) as mock_devops_platform_gateway:
        dict_args = {"remote_config_repo": "remote_repo", "image_to_scan":"image", "remote_config_branch": ""}
        token = "token"
        tool = "tool"
        mock_handle_remote_config_patterns.process_handle_working_directory.return_value = (
            "working_dir"
        )
        mock_handle_remote_config_patterns.process_handle_skip_tool.return_value = False
        mock_handle_remote_config_patterns.process_handle_analysis_pattern.return_value = (
            False
        )
        mock_container_sca_scan.process.return_value = "scan_result.json"

        mock_devops_platform_gateway.get_remote_config.return_value = remote_config

        deserialized, core_input, sbom_components = init_engine_sca_rm(
            Mock(),
            mock_devops_platform_gateway,
            Mock(),
            Mock(),
            Mock(),
            dict_args,
            token,
            tool,
        )
        assert deserialized == []
        mock_container_sca_scan.assert_not_called()


def test_init_engine_sca_rm_empty_remote_config():
    with patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.ContainerScaScan"
    ) as mock_container_sca_scan, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.SetInputCore"
    ) as mock_set_input_core, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.entry_points.entry_point_tool.HandleRemoteConfigPatterns"
    ) as mock_handle_remote_config_patterns, patch(
        "devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway"
    ) as mock_devops_platform_gateway:
        dict_args = {"remote_config_repo": "remote_repo", "image_to_scan":"image", "remote_config_branch": ""}
        token = "token"
        tool = "tool"
        mock_handle_remote_config_patterns.process_handle_working_directory.return_value = (
            "working_dir"
        )
        mock_handle_remote_config_patterns.process_handle_skip_tool.return_value = False
        mock_handle_remote_config_patterns.process_handle_analysis_pattern.return_value = (
            True
        )
        mock_container_sca_scan.process.return_value = "scan_result.json"
        
        mock_devops_platform_gateway.get_remote_config.return_value = {}

        deserialized, core_input, sbom_components = init_engine_sca_rm(
            Mock(),
            mock_devops_platform_gateway,
            Mock(),
            Mock(),
            Mock(),
            dict_args,
            token,
            tool,
        )
