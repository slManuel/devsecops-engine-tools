import unittest
from unittest.mock import Mock, patch
from devsecops_engine_tools.engine_utilities.copacetic.src.domain.usecases.copacetic import Copacetic
from devsecops_engine_tools.engine_core.src.domain.model.input_core import InputCore


class TestCopacetic(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.vulnerability_management_gateway = Mock()
        self.secrets_manager_gateway = Mock()
        self.devops_platform_gateway = Mock()
        self.remote_config_source_gateway = Mock()
        self.copacetic_gateway = Mock()
        
        # Mock configuration
        self.mock_config = {
            "TIMEOUT": 1800,
            "BUILDKIT_CONFIG": {
                "DEFAULT_ADDR": "tcp://127.0.0.1:1234"
            }
        }
        
        # Mock the devops platform gateway methods
        self.devops_platform_gateway.get_variable.return_value = "patch"
        self.devops_platform_gateway.message.return_value = "success message"
        self.remote_config_source_gateway.get_remote_config.return_value = self.mock_config
        
        self.copacetic = Copacetic(
            self.vulnerability_management_gateway,
            self.secrets_manager_gateway,
            self.devops_platform_gateway,
            self.remote_config_source_gateway,
            self.copacetic_gateway
        )
    
    def test_init(self):
        """Test Copacetic initialization"""
        # Assert
        self.assertEqual(self.copacetic.vulnerability_management_gateway, self.vulnerability_management_gateway)
        self.assertEqual(self.copacetic.secrets_manager_gateway, self.secrets_manager_gateway)
        self.assertEqual(self.copacetic.devops_platform_gateway, self.devops_platform_gateway)
        self.assertEqual(self.copacetic.remote_config_source_gateway, self.remote_config_source_gateway)
        self.assertEqual(self.copacetic.copacetic_gateway, self.copacetic_gateway)
    
    @patch('shutil.get_terminal_size')
    @patch('builtins.print')
    def test_process_success(self, mock_print, mock_terminal_size):
        """Test successful processing"""
        # Arrange
        mock_terminal_size.return_value.columns = 80
        args = {
            "remote_config_repo": "test-repo",
            "remote_config_branch": "main",
            "image": "nginx:latest",
            "vulnerability_report": "/path/to/report.json",
            "patch_format": "trivy",
            "output_image": "nginx:latest-patched"
        }
        
        # Mock successful patching
        mock_patch_result = {
            "success": True,
            "original_image": "nginx:latest",
            "patched_image": "nginx:latest-patched",
            "vulnerabilities_patched": 5,
            "packages_updated": 3,
            "platforms_processed": ["linux/amd64"],
            "patch_details": [
                {
                    "vulnerability": "CVE-2023-1234",
                    "packages": [{"name": "libssl", "version": "1.1.1"}]
                }
            ],
            "output_file": "/path/to/output.json"
        }
        self.copacetic_gateway.patch_image.return_value = mock_patch_result
        self.copacetic_gateway.get_image_info.return_value = {
            "exists": True,
            "architecture": "amd64",
            "os": "linux",
            "size": "142MB",
            "layers": 5
        }
        
        # Act
        result = self.copacetic.process(args)
        
        # Assert
        self.assertIsInstance(result, InputCore)
        self.assertEqual(result.custom_message_break_build, "Copacetic patching completed for nginx:latest")
        self.assertEqual(result.path_file_results, "/path/to/output.json")
        
        # Verify patching methods were called
        self.copacetic_gateway.patch_image.assert_called_once()
        self.copacetic_gateway.get_image_info.assert_called_once_with("nginx:latest")
    
    @patch('builtins.print')
    def test_process_missing_image(self, mock_print):
        """Test process with missing image"""
        # Arrange
        args = {
            "remote_config_repo": "test-repo",
            "remote_config_branch": "main",
            "vulnerability_report": "/path/to/report.json"
        }
        
        # Act
        result = self.copacetic.process(args)
        
        # Assert - Should return None due to exception handling, but message should be printed
        self.assertIsNone(result)
        self.devops_platform_gateway.message.assert_called()
    
    @patch('builtins.print')
    def test_process_patch_failure(self, mock_print):
        """Test processing when patching fails"""
        # Arrange
        args = {
            "remote_config_repo": "test-repo",
            "remote_config_branch": "main",
            "image": "nginx:latest",
            "vulnerability_report": "/path/to/report.json",
            "patch_format": "trivy"
        }
        
        # Mock failed patching
        mock_patch_result = {
            "success": False,
            "error": "Patching failed",
            "copa_error": "Copa command failed"
        }
        self.copacetic_gateway.patch_image.return_value = mock_patch_result
        self.copacetic_gateway.get_image_info.return_value = {"exists": True}
        
        # Act
        result = self.copacetic.process(args)
        
        # Assert - Implementation always returns InputCore, even on failure
        self.assertIsInstance(result, InputCore)
        self.assertEqual(result.custom_message_break_build, "Copacetic patching completed for nginx:latest")
        # Verify error message was printed
        self.devops_platform_gateway.message.assert_called_with("error", 
                                                                "Copacetic patching failed for nginx:latest: Patching failed\nCopa stderr: Copa command failed")
    
    @patch('builtins.print')
    def test_process_exception_handling(self, mock_print):
        """Test exception handling in process method"""
        # Arrange
        args = {
            "remote_config_repo": "test-repo",
            "remote_config_branch": "main",
            "image": "nginx:latest"
        }
        
        # Mock exception
        self.copacetic_gateway.patch_image.side_effect = Exception("Test exception")
        
        # Act
        result = self.copacetic.process(args)
        
        # Assert - Exception handling returns None, error message is logged and printed
        self.assertIsNone(result)
        self.devops_platform_gateway.message.assert_called_with("error", "Error in Copacetic process: Test exception")
    
    @patch('shutil.get_terminal_size')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.domain.usecases.copacetic.logger')
    def test_summary_printing(self, mock_logger, mock_terminal_size):
        """Test that summary is properly printed using table format"""
        # Arrange
        mock_terminal_size.return_value.columns = 100
        args = {
            "remote_config_repo": "test-repo",
            "remote_config_branch": "main",
            "image": "nginx:latest",
            "vulnerability_report": "/path/to/report.json"
        }
        
        mock_patch_result = {
            "success": True,
            "original_image": "nginx:latest",
            "patched_image": "nginx:latest-patched",
            "vulnerabilities_patched": 3,
            "packages_updated": 2,
            "platforms_processed": ["linux/amd64"],
            "patch_details": [
                {
                    "vulnerability": "CVE-2023-1234",
                    "packages": [{"name": "package1", "version": "1.0.1"}]
                }
            ],
            "output_file": "/path/to/output.json"
        }
        self.copacetic_gateway.patch_image.return_value = mock_patch_result
        self.copacetic_gateway.get_image_info.return_value = {"exists": False}
        
        # Act
        self.copacetic.process(args)
        
        # Assert
        # Check that table formatting elements were logged
        logged_calls = [call[0][0] for call in mock_logger.info.call_args_list if call[0]]
        table_elements = [call for call in logged_calls if "=" in str(call)]
        self.assertTrue(len(table_elements) >= 2)  # At least header and footer separators
    
    @patch('shutil.get_terminal_size')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.domain.usecases.copacetic.logger')
    def test_print_results_table_with_image_info(self, mock_logger, mock_terminal_size):
        """Test _print_results_table method with image info"""
        # Arrange
        mock_terminal_size.return_value.columns = 80
        
        summary = {
            "original_image": "nginx:latest",
            "patched_image": "nginx:latest-patched",
            "vulnerabilities_patched": 2,
            "packages_updated": 3,
            "platforms_processed": ["linux/amd64"],
            "patch_details": [
                {
                    "vulnerability": "CVE-2023-1234",
                    "packages": [{"name": "libssl", "version": "1.1.1"}]
                }
            ],
            "original_image_info": {
                "architecture": "amd64",
                "os": "linux",
                "size": "142MB",
                "layers": 5
            }
        }
        
        # Act
        self.copacetic._print_results_table(summary)
        
        # Assert
        logged_calls = [str(call[0][0]) for call in mock_logger.info.call_args_list if call[0]]
        
        # Check for key elements
        self.assertTrue(any("COPACETIC PATCHING RESULTS" in call for call in logged_calls))
        self.assertTrue(any("Original Image: nginx:latest" in call for call in logged_calls))
        self.assertTrue(any("Patched Image:  nginx:latest-patched" in call for call in logged_calls))
        self.assertTrue(any("Vulnerabilities Patched: 2" in call for call in logged_calls))
        self.assertTrue(any("Architecture: amd64" in call for call in logged_calls))
        self.assertTrue(any("CVE-2023-1234" in call for call in logged_calls))
    
    @patch('shutil.get_terminal_size')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.domain.usecases.copacetic.logger')
    def test_print_results_table_no_vulnerabilities(self, mock_logger, mock_terminal_size):
        """Test _print_results_table with no vulnerabilities patched"""
        # Arrange
        mock_terminal_size.return_value.columns = 80
        
        summary = {
            "original_image": "nginx:latest",
            "patched_image": "nginx:latest-patched",
            "vulnerabilities_patched": 0,
            "packages_updated": 0,
            "platforms_processed": [],
            "patch_details": [],
            "vex_file_generated": True
        }
        
        # Act
        self.copacetic._print_results_table(summary)
        
        # Assert
        logged_calls = [str(call[0][0]) for call in mock_logger.info.call_args_list if call[0]]
        self.assertTrue(any("Status: COMPLETED - No vulnerabilities found to patch" in call for call in logged_calls))


if __name__ == '__main__':
    unittest.main()
