import unittest
from unittest.mock import Mock, patch
import json
from devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.driven_adapters.copacetic.copacetic_adapter import CopaceticAdapter

class TestCopaceticAdapter(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "COPA_VERSION": "0.11.1",
            "BUILDKIT_CONFIG": {
                "DEFAULT_ADDR": "tcp://127.0.0.1:1234",
                "PROGRESS": "auto",
                "IGNORE_ERRORS": False
            },
            "TIMEOUT": 1800,
            "DEFAULT_OUTPUT_SUFFIX": "-patched"
        }
        self.adapter = CopaceticAdapter(self.config)
    
    def test_init_with_config(self):
        """Test initialization with config"""
        # Assert
        self.assertEqual(self.adapter.config, self.config)
    
    def test_init_without_config(self):
        """Test initialization without config"""
        # Act
        adapter = CopaceticAdapter()
        
        # Assert
        self.assertEqual(adapter.config, {})
    
    @patch('subprocess.run')
    @patch('platform.system')
    @patch('platform.machine')
    @patch('requests.get')
    @patch('tarfile.open')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.chmod')
    @patch('os.unlink')
    def test_install_tool_linux_amd64(self, mock_unlink, mock_chmod, mock_exists, 
                                      mock_makedirs, mock_temp_file, mock_tarfile_open, 
                                      mock_requests_get, mock_machine, mock_system, mock_run):
        """Test installing Copa tool on Linux AMD64"""
        # Arrange
        mock_run.return_value.returncode = 1  # Copa not installed
        mock_system.return_value = "Linux"
        mock_machine.return_value = "x86_64"
        mock_exists.return_value = False
        
        mock_response = Mock()
        mock_response.content = b"fake_tarball_content"
        mock_requests_get.return_value = mock_response
        mock_response.raise_for_status = Mock()
        
        mock_temp_file_obj = Mock()
        mock_temp_file_obj.name = "/tmp/fake_temp.tar.gz"
        mock_temp_file.__enter__ = Mock(return_value=mock_temp_file_obj)
        mock_temp_file.__exit__ = Mock(return_value=None)
        
        mock_tar = Mock()
        mock_member = Mock()
        mock_member.name = "copa"
        mock_member.isfile.return_value = True
        mock_tar.getmembers.return_value = [mock_member]
        mock_tarfile_open.return_value.__enter__.return_value = mock_tar
        
        # Act
        result = self.adapter.install_tool("0.11.1", "/test/path")
        
        # Assert
        mock_requests_get.assert_called_once()
        expected_url = "https://github.com/project-copacetic/copacetic/releases/download/v0.11.1/copa_0.11.1_linux_amd64.tar.gz"
        mock_requests_get.assert_called_with(expected_url, allow_redirects=True)
    
    @patch('subprocess.run')
    @patch('platform.system')
    @patch('platform.machine')
    @patch('requests.get')
    @patch('tarfile.open')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.chmod')
    @patch('os.unlink')
    def test_install_tool_linux_arm64(self, mock_unlink, mock_chmod, mock_exists, 
                                      mock_makedirs, mock_temp_file, mock_tarfile_open, 
                                      mock_requests_get, mock_machine, mock_system, mock_run):
        """Test installing Copa tool on Linux ARM64"""
        # Arrange
        mock_run.return_value.returncode = 1  # Copa not installed
        mock_system.return_value = "Linux"
        mock_machine.return_value = "aarch64"
        mock_exists.return_value = False
        
        mock_response = Mock()
        mock_response.content = b"fake_tarball_content"
        mock_requests_get.return_value = mock_response
        mock_response.raise_for_status = Mock()
        
        mock_temp_file_obj = Mock()
        mock_temp_file_obj.name = "/tmp/fake_temp.tar.gz"
        mock_temp_file.__enter__ = Mock(return_value=mock_temp_file_obj)
        mock_temp_file.__exit__ = Mock(return_value=None)
        
        mock_tar = Mock()
        mock_member = Mock()
        mock_member.name = "copa"
        mock_member.isfile.return_value = True
        mock_tar.getmembers.return_value = [mock_member]
        mock_tarfile_open.return_value.__enter__.return_value = mock_tar
        
        # Act
        result = self.adapter.install_tool("0.11.1", "/test/path")
        
        # Assert
        expected_url = "https://github.com/project-copacetic/copacetic/releases/download/v0.11.1/copa_0.11.1_linux_arm64.tar.gz"
        mock_requests_get.assert_called_with(expected_url, allow_redirects=True)
    
    @patch('subprocess.run')
    @patch('platform.system')
    @patch('platform.machine')  
    @patch('requests.get')
    @patch('tarfile.open')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.chmod')
    @patch('os.unlink')
    def test_install_tool_darwin(self, mock_unlink, mock_chmod, mock_exists, 
                                mock_makedirs, mock_temp_file, mock_tarfile_open, 
                                mock_requests_get, mock_machine, mock_system, mock_run):
        """Test Copa installation on Darwin"""
        # Arrange
        mock_run.return_value.returncode = 1  # Copa not installed
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "x86_64"
        mock_exists.return_value = True
        
        mock_response = Mock()
        mock_response.content = b"fake_tarball_content"
        mock_requests_get.return_value = mock_response
        mock_response.raise_for_status = Mock()
        
        mock_temp_file_obj = Mock()
        mock_temp_file_obj.name = "/tmp/fake_temp.tar.gz"
        mock_temp_file.__enter__ = Mock(return_value=mock_temp_file_obj)
        mock_temp_file.__exit__ = Mock(return_value=None)
        
        mock_tar = Mock()
        mock_member = Mock()
        mock_member.name = "copa"
        mock_member.isfile.return_value = True
        mock_tar.getmembers.return_value = [mock_member]
        mock_tarfile_open.return_value.__enter__.return_value = mock_tar
        
        # Act
        result = self.adapter.install_tool("0.11.1", "/test/path")
        
        # Assert
        expected_url = "https://github.com/project-copacetic/copacetic/releases/download/v0.11.1/copa_0.11.1_darwin_amd64.tar.gz"
        mock_requests_get.assert_called_with(expected_url, allow_redirects=True)
    
    @patch('subprocess.run')
    def test_install_tool_already_installed(self, mock_run):
        """Test when Copa is already installed"""
        # Arrange
        mock_run.return_value.returncode = 0  # Copa already installed
        
        # Act
        result = self.adapter.install_tool("0.11.1", "/test/path")
        
        # Assert
        self.assertIsNone(result)
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_install_tool_unsupported_os(self, mock_system, mock_run):
        """Test installing on unsupported OS"""
        # Arrange
        mock_run.return_value.returncode = 1  # Copa not installed
        mock_system.return_value = "Windows"
        
        # Act & Assert
        result = self.adapter.install_tool("0.11.1", "/test/path")
        self.assertIsNone(result)
    
    @patch('subprocess.run')
    def test_patch_image_success(self, mock_run):
        """Test successful image patching"""
        # Arrange
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Patching completed successfully"
        mock_run.return_value.stderr = ""
        
        # Mock the install_tool method to avoid actual installation
        with patch.object(self.adapter, 'install_tool', return_value="/fake/copa/path"):
            # Act
            result = self.adapter.patch_image(
                image="nginx:latest",
                vulnerability_report="/path/to/report.json",
                output_image="nginx:latest-patched",
                patch_format="trivy",
                config=self.config,
                work_folder="/test"
            )
        
        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["patched_image"], "nginx:latest-patched")
    
    @patch('subprocess.run')
    def test_patch_image_failure(self, mock_run):
        """Test failed image patching"""
        # Arrange
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "Patching failed"
        mock_run.return_value.stderr = "Error: Could not patch image"
        
        # Mock the install_tool method to avoid actual installation
        with patch.object(self.adapter, 'install_tool', return_value="/fake/copa/path"):
            # Act
            result = self.adapter.patch_image(
                image="nginx:latest",
                vulnerability_report="/path/to/report.json",
                config=self.config,
                work_folder="/test"
            )
        
        # Assert
        self.assertFalse(result["success"])
        self.assertIn("Copa command failed", result["error"])
    
    @patch('builtins.open')
    @patch('json.load')
    def test_parse_copa_output_success(self, mock_json_load, mock_open):
        """Test parsing Copa output successfully"""
        # Arrange
        mock_vex_data = {
            "statements": [
                {
                    "vulnerability": {"@id": "CVE-2023-1234"},
                    "status": "fixed",
                    "products": [
                        {
                            "@id": "pkg:deb/debian/libssl1.1@1.1.1n-0+deb11u5?arch=amd64",
                            "subcomponents": [
                                {"@id": "pkg:deb/debian/libssl1.1@1.1.1n-0+deb11u5?arch=amd64"}
                            ]
                        }
                    ]
                },
                {
                    "vulnerability": {"@id": "CVE-2023-5678"},
                    "status": "not_affected",
                    "products": []
                }
            ]
        }
        mock_json_load.return_value = mock_vex_data
        
        # Act
        result = self.adapter._parse_copa_output("/fake/output.json")
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result["vulnerabilities_patched"], 1)  # Only "fixed" status counts
        self.assertIn("details", result)
        self.assertIn("packages_updated", result)
        self.assertIn("platforms_processed", result)
        self.assertIn("amd64", result["platforms_processed"])
    
    @patch('builtins.print')  
    def test_parse_copa_output_empty(self, mock_print):
        """Test parsing empty Copa output file that doesn't exist"""
        # Act
        result = self.adapter._parse_copa_output("/nonexistent/file.json")
        
        # Assert
        self.assertEqual(result["vulnerabilities_patched"], 0)
        self.assertEqual(result["details"], [])
        self.assertEqual(result["packages_updated"], 0)
        self.assertEqual(result["platforms_processed"], [])
    
    @patch('subprocess.run')
    def test_get_image_info_success(self, mock_run):
        """Test getting image info successfully"""
        # Arrange
        mock_docker_output = json.dumps([{
            "Created": "2023-01-01T00:00:00Z",
            "Architecture": "amd64",
            "Os": "linux",
            "Size": 1234567,
            "RootFS": {"Layers": ["layer1", "layer2", "layer3"]},
            "Config": {"Env": ["PATH=/usr/bin"]}
        }])
        
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = mock_docker_output
        
        # Act
        result = self.adapter.get_image_info("nginx:latest")
        
        # Assert
        self.assertTrue(result["exists"])
        self.assertEqual(result["architecture"], "amd64")
        self.assertEqual(result["os"], "linux")
        self.assertEqual(result["layers"], 3)
    
    @patch('subprocess.run')
    def test_get_image_info_not_found(self, mock_run):
        """Test getting info for non-existent image"""
        # Arrange
        mock_run.return_value.returncode = 1
        
        # Act
        result = self.adapter.get_image_info("nonexistent:latest")
        
        # Assert
        self.assertFalse(result["exists"])


if __name__ == '__main__':
    unittest.main()
