import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from devsecops_engine_tools.engine_core.src.domain.model.finding import Finding, Category
from devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.all_tools.all_tools_deserealizator import AllToolsSecretScanDeserealizator

class TestAllToolsSecretScanDeserealizator(unittest.TestCase):

    def setUp(self):
        self.deserealizator = AllToolsSecretScanDeserealizator()
        self.deserealizator.gitleaks_deserealizator = MagicMock()
        self.deserealizator.trufflehog_deserealizator = MagicMock()
        
        # Dummy data for Finding objects
        self.finding_data = {
            "id": "test-id",
            "cvss": "0.0",
            "description": "Test secret",
            "severity": "High",
            "identification_date": "2025-12-12",
            "published_date_cve": "",
            "module": "test-module",
            "category": Category.VULNERABILITY,
            "requirements": "",
            "tool": "test-tool"
        }

    def test_get_list_vulnerability_no_duplicates(self):
        """
        Test deserialization when there are no duplicate findings.
        """
        results_scan_list = [{"gitleaks": ["g_finding1"], "trufflehog": ["t_finding1"]}]
        path_directory = "/app"
        os_env = "linux"

        finding_gitleaks = Finding(where="file1.py, Secret: sec***ret", **self.finding_data)
        finding_trufflehog = Finding(where="file2.py, Secret: ano***her", **self.finding_data)

        self.deserealizator.gitleaks_deserealizator.get_list_vulnerability.return_value = [finding_gitleaks]
        self.deserealizator.trufflehog_deserealizator.get_list_vulnerability.return_value = [finding_trufflehog]

        vulnerabilities = self.deserealizator.get_list_vulnerability(results_scan_list, path_directory, os_env)

        self.assertEqual(len(vulnerabilities), 2)
        self.assertIn(finding_gitleaks, vulnerabilities)
        self.assertIn(finding_trufflehog, vulnerabilities)
        self.deserealizator.gitleaks_deserealizator.get_list_vulnerability.assert_called_once_with(
            ["g_finding1"], path_directory, os_env
        )
        self.deserealizator.trufflehog_deserealizator.get_list_vulnerability.assert_called_once_with(
            ["t_finding1"], os_env, path_directory
        )

    def test_get_list_vulnerability_with_duplicates(self):
        """
        Test that duplicate findings (based on 'where' field) are removed, prioritizing Gitleaks.
        """
        results_scan_list = [{"gitleaks": ["g_finding1"], "trufflehog": ["t_finding_dup"]}]
        path_directory = "/app"
        os_env = "linux"

        finding_gitleaks = Finding(where="file1.py, Secret: sec***ret", **self.finding_data)
        finding_trufflehog_dup = Finding(where="/file1.py, Secret: sec***ret", **self.finding_data)

        self.deserealizator.gitleaks_deserealizator.get_list_vulnerability.return_value = [finding_gitleaks]
        self.deserealizator.trufflehog_deserealizator.get_list_vulnerability.return_value = [finding_trufflehog_dup]

        vulnerabilities = self.deserealizator.get_list_vulnerability(results_scan_list, path_directory, os_env)

        self.assertEqual(len(vulnerabilities), 1)
        self.assertIn(finding_gitleaks, vulnerabilities)
        self.assertNotIn(finding_trufflehog_dup, vulnerabilities)

    def test_get_list_vulnerability_only_gitleaks(self):
        """
        Test deserialization when only Gitleaks results are present.
        """
        results_scan_list = [{"gitleaks": ["g_finding1"], "trufflehog": []}]
        path_directory = "/app"
        os_env = "linux"

        finding_gitleaks = Finding(where="file1.py, Secret: sec***ret", **self.finding_data)
        self.deserealizator.gitleaks_deserealizator.get_list_vulnerability.return_value = [finding_gitleaks]
        self.deserealizator.trufflehog_deserealizator.get_list_vulnerability.return_value = []

        vulnerabilities = self.deserealizator.get_list_vulnerability(results_scan_list, path_directory, os_env)

        self.assertEqual(len(vulnerabilities), 1)
        self.assertIn(finding_gitleaks, vulnerabilities)

    def test_normalize_where(self):
        """
        Test the _normalize_where method extracts detector, filename, and secret.
        New format: detector|filename|secret (path-agnostic deduplication)
        """
        # Test with full where string from Gitleaks format
        self.assertEqual(self.deserealizator._normalize_where("file.py, Secret: sec*********ret"), "|file.py|sec*********ret")
        # Test with detector and secret
        self.assertEqual(self.deserealizator._normalize_where("/path/to/file.py, Detector: github-pat, Secret: ghp*********xYZ"), "github-pat|file.py|ghp*********xYZ")
        # Test with empty string
        self.assertEqual(self.deserealizator._normalize_where(""), "")

    def test_get_where_correctly(self):
        """
        Test the get_where_correctly method formats the 'where' string as expected.
        """
        path_directory = "/app/"
        result = {
            "File": "/app/config/settings.py",
            "Secret": "superlongsecretvalue"
        }
        
        expected_where = "config/settings.py, Secret: sup*********lue"
        actual_where = self.deserealizator.get_where_correctly(result, path_directory)
        
        self.assertEqual(actual_where, expected_where)

    def test_get_where_correctly_no_path_directory(self):
        """
        Test get_where_correctly when path_directory is empty.
        """
        result = {
            "File": "config/settings.py",
            "Secret": "superlongsecretvalue"
        }
        
        expected_where = "config/settings.py, Secret: sup*********lue"
        actual_where = self.deserealizator.get_where_correctly(result, "")
        
        self.assertEqual(actual_where, expected_where)

if __name__ == '__main__':
    unittest.main()
