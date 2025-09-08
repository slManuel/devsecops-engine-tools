import unittest
from unittest.mock import MagicMock, patch
from devsecops_engine_tools.engine_utilities.sonarqube.src.applications.runner_report_sonar import runner_report_sonar

class TestRunnerReportSonar(unittest.TestCase):
    @patch(
        "devsecops_engine_tools.engine_utilities.sonarqube.src.applications.runner_report_sonar.SonarAdapter"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.sonarqube.src.applications.runner_report_sonar.init_report_sonar"
    )
    def test_runner_report_sonar_success(self, mock_init_report_sonar, mock_sonar_adapter):
        # Arrange
        mock_vuln = MagicMock()
        mock_secrets = MagicMock()
        mock_devops = MagicMock()
        mock_remote = MagicMock()
        mock_metrics = MagicMock()
        args = {"foo": "bar"}

        # Act
        runner_report_sonar(
            vulnerability_management_gateway=mock_vuln,
            secrets_manager_gateway=mock_secrets,
            devops_platform_gateway=mock_devops,
            remote_config_source_gateway=mock_remote,
            metrics_manager_gateway=mock_metrics,
            args=args,
        )

        # Assert
        mock_sonar_adapter.assert_called_once()
        mock_init_report_sonar.assert_called_once_with(
            vulnerability_management_gateway=mock_vuln,
            secrets_manager_gateway=mock_secrets,
            devops_platform_gateway=mock_devops,
            remote_config_source_gateway=mock_remote,
            sonar_gateway=mock_sonar_adapter(),
            metrics_manager_gateway=mock_metrics,
            args=args,
        )

    @patch(
        "devsecops_engine_tools.engine_utilities.sonarqube.src.applications.runner_report_sonar.SonarAdapter"
    )
    @patch(
        "devsecops_engine_tools.engine_utilities.sonarqube.src.applications.runner_report_sonar.init_report_sonar"
    )
    def test_runner_report_sonar_exception(self, mock_init_report_sonar, mock_sonar_adapter):
        # Arrange
        mock_vuln = MagicMock()
        mock_secrets = MagicMock()
        mock_devops = MagicMock()
        mock_remote = MagicMock()
        mock_metrics = MagicMock()
        args = {"foo": "bar"}

        # Simula excepción en init_report_sonar
        mock_init_report_sonar.side_effect = Exception("fail")

        # Mock para devops_platform_gateway.message y result_pipeline
        mock_devops.message = MagicMock(return_value="error message")
        mock_devops.result_pipeline = MagicMock(return_value="failed")

        # Act
        runner_report_sonar(
            vulnerability_management_gateway=mock_vuln,
            secrets_manager_gateway=mock_secrets,
            devops_platform_gateway=mock_devops,
            remote_config_source_gateway=mock_remote,
            metrics_manager_gateway=mock_metrics,
            args=args,
        )

        # Assert
        mock_devops.message.assert_called()
        mock_devops.result_pipeline.assert_called_with("failed")