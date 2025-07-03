import unittest
from unittest.mock import patch, MagicMock
import sys
import argparse
from devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations import (
    runner_engine_integrations, get_inputs_from_cli
)

class TestRunnerEngineIntegrations(unittest.TestCase):

    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.get_inputs_from_cli"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.DefectDojoPlatform"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.SecretsManager"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.AzureDevops"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.GithubActions"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.RuntimeLocal"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.S3Manager"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.init_engine_integrations"
    )
    def test_runner_engine_integrations_success(
        self,
        mock_init_engine_integrations,
        mock_s3_manager,
        mock_runtime_local,
        mock_github_actions,
        mock_azure_devops,
        mock_secrets_manager,
        mock_defect_dojo,
        mock_get_inputs_from_cli,
    ):
        # Arrange
        args = {
            "integration": "report_sonar",
            "remote_config_repo": "repo",
            "remote_config_branch": "main",
            "platform_devops": "azure",
            "remote_config_source": "azure",
            "use_secrets_manager": "true",
            "send_metrics": "true",
            "sonar_url": "http://sonar",
            "sonar_instance": "sonar",
            "token_cmdb": "cmdb",
            "token_vulnerability_management": "vm",
            "token_sonar": "sonar_token",
        }
        mock_get_inputs_from_cli.return_value = args
        mock_defect_dojo.return_value = MagicMock()
        mock_secrets_manager.return_value = MagicMock()
        mock_azure_devops.return_value = MagicMock()
        mock_github_actions.return_value = MagicMock()
        mock_runtime_local.return_value = MagicMock()
        mock_s3_manager.return_value = MagicMock()

        # Act
        runner_engine_integrations()

        # Assert
        mock_init_engine_integrations.assert_called_once()
        self.assertTrue(mock_get_inputs_from_cli.called)

    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.get_inputs_from_cli"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.DefectDojoPlatform"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.SecretsManager"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.AzureDevops"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.GithubActions"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.RuntimeLocal"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.S3Manager"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.engine_integrations.src.applications.runner_engine_integrations.init_engine_integrations"
    )
    def test_runner_engine_integrations_exception(
        self,
        mock_init_engine_integrations,
        mock_s3_manager,
        mock_runtime_local,
        mock_github_actions,
        mock_azure_devops,
        mock_secrets_manager,
        mock_defect_dojo,
        mock_get_inputs_from_cli,
    ):
        # Arrange
        args = {
            "integration": "report_sonar",
            "remote_config_repo": "repo",
            "remote_config_branch": "main",
            "platform_devops": "azure",
            "remote_config_source": "azure",
            "use_secrets_manager": "true",
            "send_metrics": "true",
            "sonar_url": "http://sonar",
            "sonar_instance": "sonar",
            "token_cmdb": "cmdb",
            "token_vulnerability_management": "vm",
            "token_sonar": "sonar_token",
        }
        mock_get_inputs_from_cli.return_value = args
        mock_defect_dojo.return_value = MagicMock()
        mock_secrets_manager.return_value = MagicMock()
        mock_azure_devops.return_value = MagicMock()
        mock_github_actions.return_value = MagicMock()
        mock_runtime_local.return_value = MagicMock()
        mock_s3_manager.return_value = MagicMock()
        mock_init_engine_integrations.side_effect = Exception("fail")

        # Mock para devops_platform_gateway.message y result_pipeline
        devops_platform_gateway_mock = MagicMock()
        devops_platform_gateway_mock.message.return_value = "error message"
        devops_platform_gateway_mock.result_pipeline.return_value = "failed"
        # For platform_devops = "azure"
        mock_azure_devops.return_value = devops_platform_gateway_mock

        # Act
        runner_engine_integrations()

        # Assert
        devops_platform_gateway_mock.message.assert_called()
        devops_platform_gateway_mock.result_pipeline.assert_called_with("failed")

    @patch(
        "argparse.ArgumentParser.parse_args"
    )
    def test_get_inputs_from_cli(self, mock_parse_args):
        # Arrange
        mock_parse_args.return_value = argparse.Namespace(
            integration="report_sonar",
            remote_config_repo="test_repo",
            remote_config_branch="test_branch",
            platform_devops="azure",
            remote_config_source="azure",
            use_secrets_manager="false",
            send_metrics="true",
            sonar_url="https://sonar.com/",
            sonar_instance="test_sonar_instance",
            token_cmdb="my_token_cmdb",
            token_vulnerability_management="my_token_vm",
            token_sonar="my_token_sonar"
        )

        expected_output = {
            "integration": "report_sonar",
            "remote_config_repo": "test_repo",
            "remote_config_branch": "test_branch",
            "platform_devops": "azure",
            "remote_config_source": "azure",
            "use_secrets_manager": "false",
            "send_metrics": "true",
            "sonar_url": "https://sonar.com/",
            "sonar_instance": "test_sonar_instance",
            "token_cmdb": "my_token_cmdb",
            "token_vulnerability_management": "my_token_vm",
            "token_sonar": "my_token_sonar"
        }

        # Act
        result = get_inputs_from_cli(sys.argv[1:])

        # Assert
        self.assertEqual(result, expected_output)