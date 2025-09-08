import unittest
from unittest.mock import MagicMock, patch

from devsecops_engine_tools.engine_integrations.src.domain.usecases.handle_integrations import Integrations

class TestIntegrations(unittest.TestCase):

    @patch(
        "devsecops_engine_tools.engine_integrations.src.domain.usecases.handle_integrations.runner_report_sonar"
    )
    def test_process_report_sonar(self, mock_runner_report_sonar):
        # Arrange
        mock_vuln = MagicMock()
        mock_secrets = MagicMock()
        mock_devops = MagicMock()
        mock_remote = MagicMock()
        mock_metrics = MagicMock()
        args = {"integration": "report_sonar", "foo": "bar"}

        integrations = Integrations(
            vulnerability_management_gateway=mock_vuln,
            secrets_manager_gateway=mock_secrets,
            devops_platform_gateway=mock_devops,
            remote_config_source_gateway=mock_remote,
            metrics_manager_gateway=mock_metrics,
        )

        mock_runner_report_sonar.return_value = "sonar_result"

        # Act
        result = integrations.process(args)

        # Assert
        mock_runner_report_sonar.assert_called_once_with(
            vulnerability_management_gateway=mock_vuln,
            secrets_manager_gateway=mock_secrets,
            devops_platform_gateway=mock_devops,
            remote_config_source_gateway=mock_remote,
            metrics_manager_gateway=mock_metrics,
            args=args,
        )
        self.assertEqual(result, "sonar_result")

    def test_process_other_integration(self):
        # Arrange
        mock_vuln = MagicMock()
        mock_secrets = MagicMock()
        mock_devops = MagicMock()
        mock_remote = MagicMock()
        mock_metrics = MagicMock()
        args = {"integration": "other_integration"}

        integrations = Integrations(
            vulnerability_management_gateway=mock_vuln,
            secrets_manager_gateway=mock_secrets,
            devops_platform_gateway=mock_devops,
            remote_config_source_gateway=mock_remote,
            metrics_manager_gateway=mock_metrics,
        )

        # Act
        result = integrations.process(args)

        # Assert
        self.assertIsNone(result)
