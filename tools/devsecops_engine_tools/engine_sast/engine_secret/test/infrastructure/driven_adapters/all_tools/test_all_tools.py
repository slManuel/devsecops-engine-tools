import unittest
from unittest.mock import patch, MagicMock, call, mock_open
from devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools import AllToolsSecretScan
import json

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
        Test that run_tool_secret_scan executes both tools and combines their results without deduplication.
        """
        # Mock data
        files, agent_os, agent_work_folder, repository_name, config_tool, secret_tool, secret_external_checks, agent_temp_dir, tool, folder_path = ["file1.py"], "linux", "/app", "my-repo", {}, {}, {}, "/tmp", "all", "/app"

        gitleaks_findings = [{"finding": "gitleaks_secret", "File": "file1.py", "StartLine": 1, "Secret": "s1"}]
        gitleaks_path = "/tmp/gitleaks.json"
        trufflehog_findings = [{"finding": "trufflehog_secret"}]
        trufflehog_path = "/tmp/trufflehog.json"

        self.mock_gitleaks_tool_instance.run_tool_secret_scan.return_value = (gitleaks_findings, gitleaks_path)
        self.mock_trufflehog_tool_instance.run_tool_secret_scan.return_value = (trufflehog_findings, trufflehog_path)

        with patch.object(self.all_tools_secret_scan, '_rewrite_trufflehog_file') as mock_rewrite:
            findings, finding_path = self.all_tools_secret_scan.run_tool_secret_scan(
                files, agent_os, agent_work_folder, repository_name, 
                config_tool, secret_tool, secret_external_checks, 
                agent_temp_dir, tool, folder_path
            )

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
            mock_rewrite.assert_called_once_with(trufflehog_findings, trufflehog_path)

    @patch('devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    def test_run_tool_secret_scan_with_deduplication(self, mock_file, mock_exists):
        """
        Test that run_tool_secret_scan correctly deduplicates findings between Gitleaks and TruffleHog.
        """
        files, agent_os, agent_work_folder, repository_name, config_tool, secret_tool, secret_external_checks, agent_temp_dir, tool, folder_path = ["file1.py"], "linux", "/app", "my-repo", {}, {}, {}, "/tmp", "all", "/app"

        gitleaks_findings = [{
            "File": "/app/src/main.py", "StartLine": 42, "Secret": "AKIAIOSFODNN7EXAMPLE",
        }]
        
        trufflehog_findings = [
            {"SourceMetadata": {"Data": {"Filesystem": {"file": "/app/src/main.py", "line": 42}}}, "Raw": "AKIAIOSFODNN7EXAMPLE"},
            {"SourceMetadata": {"Data": {"Filesystem": {"file": "/app/src/utils.py", "line": 88}}}, "Raw": "another_secret_shhhh"},
        ]
        
        gitleaks_path, trufflehog_path = "/tmp/gitleaks.json", "/tmp/trufflehog.json"
        self.mock_gitleaks_tool_instance.run_tool_secret_scan.return_value = (gitleaks_findings, gitleaks_path)
        self.mock_trufflehog_tool_instance.run_tool_secret_scan.return_value = (trufflehog_findings, trufflehog_path)

        findings, _ = self.all_tools_secret_scan.run_tool_secret_scan(
            files, agent_os, agent_work_folder, repository_name, 
            config_tool, secret_tool, secret_external_checks, 
            agent_temp_dir, tool, folder_path
        )
        
        expected_trufflehog = [trufflehog_findings[1]]
        self.assertEqual(findings, [{"gitleaks": gitleaks_findings, "trufflehog": expected_trufflehog}])
        
        mock_exists.assert_called_once_with(trufflehog_path)
        mock_file.assert_called_once_with(trufflehog_path, "w")
        mock_file().writelines.assert_called_once()

    @patch('devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    def test_run_tool_secret_scan_with_internal_trufflehog_deduplication(self, mock_file, mock_exists):
        """
        Test that run_tool_secret_scan correctly deduplicates findings within TruffleHog results.
        """
        files, agent_os, agent_work_folder, repository_name, config_tool, secret_tool, secret_external_checks, agent_temp_dir, tool, folder_path = [], "linux", "/app", "repo", {}, {}, {}, "/tmp", "all", "/app"
        gitleaks_findings, gitleaks_path = [], "/tmp/gitleaks.json"
        trufflehog_findings = [
            {"SourceMetadata": {"Data": {"Filesystem": {"file": "/app/config.yml", "line": 15}}}, "Raw": "password123"},
            {"SourceMetadata": {"Data": {"Filesystem": {"file": "/app/config.yml", "line": 15}}}, "Raw": "password123"},
            {"SourceMetadata": {"Data": {"Filesystem": {"file": "/app/settings.py", "line": 10}}}, "Raw": "secret_key"}
        ]
        trufflehog_path = "/tmp/trufflehog.json"

        self.mock_gitleaks_tool_instance.run_tool_secret_scan.return_value = (gitleaks_findings, gitleaks_path)
        self.mock_trufflehog_tool_instance.run_tool_secret_scan.return_value = (trufflehog_findings, trufflehog_path)

        findings, _ = self.all_tools_secret_scan.run_tool_secret_scan(
            files, agent_os, agent_work_folder, repository_name, 
            config_tool, secret_tool, secret_external_checks, 
            agent_temp_dir, tool, folder_path
        )
        expected_trufflehog = [trufflehog_findings[0], trufflehog_findings[2]]
        self.assertEqual(len(findings[0]["trufflehog"]), 2)
        self.assertEqual(findings[0]["trufflehog"], expected_trufflehog)

    @patch('devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools.logger')
    def test_run_tool_secret_scan_with_deduplication_error(self, mock_logger):
        """
        Test that run_tool_secret_scan handles exceptions during deduplication.
        """
        files, agent_os, agent_work_folder, repository_name, config_tool, secret_tool, secret_external_checks, agent_temp_dir, tool, folder_path = [], "linux", "/app", "repo", {}, {}, {}, "/tmp", "all", "/app"
        gitleaks_findings, gitleaks_path = [{"finding": "gitleaks_secret"}], "/tmp/gitleaks.json"
        trufflehog_findings, trufflehog_path = [{"finding": "trufflehog_secret"}], "/tmp/trufflehog.json"
        self.mock_gitleaks_tool_instance.run_tool_secret_scan.return_value = (gitleaks_findings, gitleaks_path)
        self.mock_trufflehog_tool_instance.run_tool_secret_scan.return_value = (trufflehog_findings, trufflehog_path)
        
        exception_message = "Deduplication failed"
        with patch.object(self.all_tools_secret_scan, '_normalize_for_cross_tool_dedup', side_effect=Exception(exception_message)):
            findings, _ = self.all_tools_secret_scan.run_tool_secret_scan(
                files, agent_os, agent_work_folder, repository_name, 
                config_tool, secret_tool, secret_external_checks, 
                agent_temp_dir, tool, folder_path
            )
            self.assertEqual(findings, [{"gitleaks": gitleaks_findings, "trufflehog": trufflehog_findings}])
            mock_logger.error.assert_called_with(f"Error during deduplication: {exception_message}")

    def test_run_tool_secret_scan_one_tool_empty(self):
        """Test run_tool_secret_scan when one of the tools returns no findings."""
        files, agent_os, agent_work_folder, repository_name, config_tool, secret_tool, secret_external_checks, agent_temp_dir, tool, folder_path = [], "linux", "/app", "repo", {}, {}, {}, "/tmp", "all", "/app"
        gitleaks_findings, gitleaks_path = [], "/tmp/gitleaks.json"
        trufflehog_findings, trufflehog_path = [{"finding": "trufflehog_secret"}], "/tmp/trufflehog.json"
        self.mock_gitleaks_tool_instance.run_tool_secret_scan.return_value = (gitleaks_findings, gitleaks_path)
        self.mock_trufflehog_tool_instance.run_tool_secret_scan.return_value = (trufflehog_findings, trufflehog_path)

        with patch.object(self.all_tools_secret_scan, '_rewrite_trufflehog_file') as mock_rewrite:
            findings, finding_path = self.all_tools_secret_scan.run_tool_secret_scan(
                files, agent_os, agent_work_folder, repository_name, 
                config_tool, secret_tool, secret_external_checks, 
                agent_temp_dir, tool, folder_path
            )
            self.assertEqual(findings, [{"gitleaks": [], "trufflehog": trufflehog_findings}])
            self.assertEqual(finding_path, f"{gitleaks_path}#{trufflehog_path}")
            mock_rewrite.assert_called_once_with(trufflehog_findings, trufflehog_path)

    @patch('devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools.logger')
    def test_rewrite_trufflehog_file(self, mock_logger, mock_file, mock_exists):
        """Test the _rewrite_trufflehog_file method."""
        mock_exists.return_value = True
        findings, file_path = [{"key": "value"}], "/tmp/truffle.json"
        self.all_tools_secret_scan._rewrite_trufflehog_file(findings, file_path)
        mock_file.assert_called_with(file_path, "w")
        mock_file().writelines.assert_called_once()

        mock_file.reset_mock()
        self.all_tools_secret_scan._rewrite_trufflehog_file(findings, "")
        mock_file.assert_not_called()

        mock_file.reset_mock()
        mock_exists.return_value = False
        self.all_tools_secret_scan._rewrite_trufflehog_file(findings, file_path)
        mock_exists.assert_called_with(file_path)
        mock_file.assert_not_called()
        
        mock_file.reset_mock()
        mock_exists.return_value = True
        exception_message = "Permission denied"
        mock_file.side_effect = Exception(exception_message)
        self.all_tools_secret_scan._rewrite_trufflehog_file(findings, file_path)
        mock_logger.error.assert_any_call(f"Error rewriting TruffleHog file: {exception_message}")

    def test_mask_secret(self):
        """Test the _mask_secret method with various inputs."""
        self.assertEqual(self.all_tools_secret_scan._mask_secret("1234567890"), "123*********890")
        self.assertEqual(self.all_tools_secret_scan._mask_secret("12345"), "12345")
        self.assertEqual(self.all_tools_secret_scan._mask_secret("123456"), "123456")
        self.assertEqual(self.all_tools_secret_scan._mask_secret(""), "")
        self.assertEqual(self.all_tools_secret_scan._mask_secret("abc*123"), "abc*123")
        self.assertEqual(self.all_tools_secret_scan._mask_secret(1234567890), "123*********890")

    def test_deduplicate_trufflehog_internal(self):
        """Test internal deduplication of TruffleHog findings."""
        findings = [
            {"Raw": "secret1", "SourceMetadata": {"Data": {"Filesystem": {"file": "a.py", "line": 1}}}},
            {"Raw": "secret1", "SourceMetadata": {"Data": {"Filesystem": {"file": "a.py", "line": 1}}}},
            {"Raw": "secret2", "SourceMetadata": {"Data": {"Filesystem": {"file": "a.py", "line": 2}}}},
            {"Raw": "secret3", "SourceMetadata": {"Data": {"Filesystem": {"file": "b.py", "line": 1}}}},
            {"file": "c.py", "line": 1, "Raw": "secret4"},
        ]
        deduplicated = self.all_tools_secret_scan._deduplicate_trufflehog_internal(findings)
        self.assertEqual(len(deduplicated), 4)
        self.assertEqual(deduplicated[0], findings[0])
        self.assertEqual(deduplicated[1], findings[2])

    def test_deduplicate_trufflehog_internal_empty(self):
        """Test internal deduplication with empty list."""
        self.assertEqual(self.all_tools_secret_scan._deduplicate_trufflehog_internal([]), [])

    def test_normalize_for_cross_tool_dedup(self):
        """Test normalization for cross-tool deduplication."""
        gitleaks_item = {"File": "path/to/file.py", "StartLine": 10, "Secret": "secret_val"}
        trufflehog_item = {"SourceMetadata": {"Data": {"Filesystem": {"file": "path/to/file.py", "line": 10}}}, "Raw": "secret_val"}
        
        masked_secret = self.all_tools_secret_scan._mask_secret("secret_val")
        expected = f"file.py|10|{masked_secret}"
        
        self.assertEqual(self.all_tools_secret_scan._normalize_for_cross_tool_dedup(gitleaks_item, is_gitleaks=True), expected)
        self.assertEqual(self.all_tools_secret_scan._normalize_for_cross_tool_dedup(trufflehog_item, is_gitleaks=False), expected)

        expected_no_line = f"file.py|{masked_secret}"
        self.assertEqual(self.all_tools_secret_scan._normalize_for_cross_tool_dedup(gitleaks_item, is_gitleaks=True, include_line=False), expected_no_line)

        self.assertEqual(self.all_tools_secret_scan._normalize_for_cross_tool_dedup({}, is_gitleaks=True), "")
        self.assertEqual(self.all_tools_secret_scan._normalize_for_cross_tool_dedup({"File": "file.py"}, is_gitleaks=True), "file.py||")

if __name__ == '__main__':
    unittest.main()