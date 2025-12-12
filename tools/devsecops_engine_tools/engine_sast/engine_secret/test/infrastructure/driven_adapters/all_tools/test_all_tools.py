import unittest
from unittest.mock import patch, MagicMock, call
from devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools import AllToolsSecretScan

class TestAllToolsSecretScan(unittest.TestCase):

    @patch('devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools.TrufflehogRun')
    @patch('devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools.GitleaksTool')
    def setUp(self, mock_gitleaks_tool, mock_trufflehog_tool):
        self.mock_gitleaks_tool_instance = MagicMock()
        self.mock_trufflehog_tool_instance = MagicMock()
        
        mock_gitleaks_tool.return_value = self.mock_gitleaks_tool_instance
        mock_trufflehog_tool.return_value = self.mock_trufflehog_tool_instance
        
        self.all_tools_secret_scan = AllToolsSecretScan()
        self.all_tools_secret_scan.gitleaks_tool = self.mock_gitleaks_tool_instance
        self.all_tools_secret_scan.trufflehog_tool = self.mock_trufflehog_tool_instance

    def test_install_tool(self):
        """
        Test that install_tool calls the install method for both tools in parallel.
        """
        agent_os = "linux"
        agent_temp_dir = "/tmp"
        tool_version = {"GITLEAKS": "v1.0.0", "TRUFFLEHOG": "v2.0.0"}

        self.all_tools_secret_scan.install_tool(agent_os, agent_temp_dir, tool_version)

        self.mock_gitleaks_tool_instance.install_tool.assert_called_once_with(agent_os, agent_temp_dir, "v1.0.0")
        self.mock_trufflehog_tool_instance.install_tool.assert_called_once_with(agent_os, agent_temp_dir, "v2.0.0")

    @patch('devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools.logger')
    def test_install_tool_with_exception(self, mock_logger):
        """
        Test that install_tool logs an error if one of the installations fails.
        """
        agent_os = "linux"
        agent_temp_dir = "/tmp"
        tool_version = {"GITLEAKS": "v1.0.0", "TRUFFLEHOG": "v2.0.0"}
        
        exception_message = "Installation failed"
        self.mock_gitleaks_tool_instance.install_tool.side_effect = Exception(exception_message)
        self.mock_trufflehog_tool_instance.install_tool.return_value = None

        self.all_tools_secret_scan.install_tool(agent_os, agent_temp_dir, tool_version)

        self.mock_gitleaks_tool_instance.install_tool.assert_called_once_with(agent_os, agent_temp_dir, "v1.0.0")
        self.mock_trufflehog_tool_instance.install_tool.assert_called_once_with(agent_os, agent_temp_dir, "v2.0.0")
        mock_logger.error.assert_called_with(f"Error installing tool: {exception_message}")

    def test_run_tool_secret_scan(self):
        """
        Test that run_tool_secret_scan executes both tools and combines their results.
        """
        # Mock data
        files = ["file1.py", "file2.js"]
        agent_os = "linux"
        agent_work_folder = "/app"
        repository_name = "my-repo"
        config_tool = {}
        secret_tool = {}
        secret_external_checks = {}
        agent_temp_dir = "/tmp"
        tool = "all"
        folder_path = "/app"

        # Mock return values for the tool runs
        gitleaks_findings = [{"finding": "gitleaks_secret"}]
        gitleaks_path = "/tmp/gitleaks.json"
        trufflehog_findings = [{"finding": "trufflehog_secret"}]
        trufflehog_path = "/tmp/trufflehog.json"

        self.mock_gitleaks_tool_instance.run_tool_secret_scan.return_value = (gitleaks_findings, gitleaks_path)
        self.mock_trufflehog_tool_instance.run_tool_secret_scan.return_value = (trufflehog_findings, trufflehog_path)

        # Execute the method
        findings, finding_path = self.all_tools_secret_scan.run_tool_secret_scan(
            files, agent_os, agent_work_folder, repository_name, 
            config_tool, secret_tool, secret_external_checks, 
            agent_temp_dir, tool, folder_path
        )

        # Assertions
        self.mock_gitleaks_tool_instance.run_tool_secret_scan.assert_called_once_with(
            files, agent_os, agent_work_folder, repository_name, 
            config_tool, secret_tool, secret_external_checks, 
            agent_temp_dir, "gitleaks", folder_path
        )
        self.mock_trufflehog_tool_instance.run_tool_secret_scan.assert_called_once_with(
            files, agent_os, agent_work_folder, repository_name, 
            config_tool, secret_tool, secret_external_checks, 
            agent_temp_dir, "trufflehog", folder_path
        )

        expected_findings = [{"gitleaks": gitleaks_findings, "trufflehog": trufflehog_findings}]
        expected_path = f"{gitleaks_path}#{trufflehog_path}"

        self.assertEqual(findings, expected_findings)
        self.assertEqual(finding_path, expected_path)

if __name__ == '__main__':
    unittest.main()
