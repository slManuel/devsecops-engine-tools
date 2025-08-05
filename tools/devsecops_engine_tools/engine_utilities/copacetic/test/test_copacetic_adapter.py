import unittest
from unittest.mock import Mock, patch, MagicMock
from devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.driven_adapters.copacetic.copacetic_adapter import (
    CopaceticAdapter
)


class TestCopaceticAdapter(unittest.TestCase):
    
    def setUp(self):
        self.adapter = CopaceticAdapter()
    
    def test_find_copa_binary_in_path(self):
        """Test finding Copa binary in PATH"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "/usr/bin/copa"
            
            binary = self.adapter._find_copa_binary()
            self.assertEqual(binary, "copa")
    
    def test_check_copa_availability(self):
        """Test checking Copa availability"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "copa version 0.11.0"
            
            is_available = self.adapter.check_copa_availability()
            self.assertTrue(is_available)
    
    def test_get_copa_version(self):
        """Test getting Copa version"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "copa version 0.11.0"
            
            version = self.adapter.get_copa_version()
            self.assertEqual(version, "copa version 0.11.0")
    
    @patch('subprocess.run')
    @patch('tempfile.mkdtemp')
    def test_patch_image_success(self, mock_mkdtemp, mock_run):
        """Test successful image patching"""
        # Mock successful Copa execution
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Successfully patched 5 vulnerabilities"
        mock_run.return_value.stderr = ""
        
        mock_mkdtemp.return_value = "/tmp/docker_config"
        
        result = self.adapter.patch_image(
            container_image="nginx:latest",
            vulnerability_report="/path/to/report.json",
            patch_format="trivy"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["patched_image"], "nginx:latest-patched")
        self.assertIn("copa_output", result)
    
    @patch('subprocess.run')
    def test_patch_image_failure(self, mock_run):
        """Test failed image patching"""
        # Mock failed Copa execution
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Error: Could not patch image"
        
        result = self.adapter.patch_image(
            container_image="nginx:latest",
            vulnerability_report="/path/to/report.json",
            patch_format="trivy"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("Could not patch image", result["error"])
    
    def test_parse_copa_output(self):
        """Test parsing Copa output"""
        output = """
        Starting patch process...
        Successfully patched 3 vulnerabilities
        Completed patching process
        """
        
        details = self.adapter._parse_copa_output(output)
        
        self.assertEqual(details["vulnerabilities_patched"], 3)
        self.assertTrue(len(details["details"]) > 0)


if __name__ == '__main__':
    unittest.main()
