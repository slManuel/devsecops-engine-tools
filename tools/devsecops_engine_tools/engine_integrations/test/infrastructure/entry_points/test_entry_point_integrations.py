import unittest
from unittest.mock import patch, MagicMock

from devsecops_engine_tools.engine_integrations.src.infrastructure.entry_points.entry_point_integrations import (
    init_engine_integrations,
)

class TestEntryPointIntegrations(unittest.TestCase):

    @patch(
        "devsecops_engine_tools.engine_integrations.src.infrastructure.entry_points.entry_point_integrations.Integrations"
    )
    def test_init_engine_integrations_calls_process(self, mock_integrations):
        # Arrange
        mock_instance = MagicMock()
        mock_integrations.return_value = mock_instance
        mock_instance.process.return_value = "result"

        mock_vuln = MagicMock()
        mock_secrets = MagicMock()
        mock_devops = MagicMock()
        mock_remote = MagicMock()
        mock_metrics = MagicMock()
        args = {"integration": "report_sonar", "remote_config_repo": "repo", "remote_config_branch": "branch"}

        # Act
        result = init_engine_integrations(
            vulnerability_management_gateway=mock_vuln,
            secrets_manager_gateway=mock_secrets,
            devops_platform_gateway=mock_devops,
            remote_config_source_gateway=mock_remote,
            metrics_manager_gateway=mock_metrics,
            args=args,
        )

        # Assert
        mock_integrations.assert_called_once_with(
            vulnerability_management_gateway=mock_vuln,
            secrets_manager_gateway=mock_secrets,
            devops_platform_gateway=mock_devops,
            remote_config_source_gateway=mock_remote,
            metrics_manager_gateway=mock_metrics,
        )
        mock_instance.process.assert_called_once_with(args)
        self.assertEqual(result, "result")
