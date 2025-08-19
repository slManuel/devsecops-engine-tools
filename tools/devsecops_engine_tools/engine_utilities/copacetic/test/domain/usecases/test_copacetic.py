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
    
    @patch('builtins.print')
    def test_process_success(self, mock_print):
        """Test successful processing"""
        # Arrange
        args = {
            "remote_config_repo": "test-repo",
            "remote_config_branch": "main",
            "image": "nginx:latest",
            "vulnerability_report": "/path/to/report.json",
            "patch_format": "trivy",
            "scope_pipeline": "test-pipeline",
            "scope_service": "test-service",
            "stage_pipeline": "patch"
        }
        
        # Mock successful patching
        mock_patch_result = {
            "success": True,
            "patched_image": "nginx:latest-patched",
            "vulnerabilities_patched": 5,
            "packages_updated": 3,
            "platforms_processed": ["linux/amd64"],
            "patch_details": ["Updated package1", "Updated package2"],
            "output_format": "openvex",
            "output_file": "/path/to/output.json"
        }
        self.copacetic_gateway.patch_image.return_value = mock_patch_result
        self.copacetic_gateway.get_image_info.return_value = {
            "exists": True,
            "architecture": "amd64",
            "os": "linux",
            "layers": 5
        }
        
        # Act
        result = self.copacetic.process(args)
        
        # Assert
        self.assertIsInstance(result, InputCore)
        self.assertEqual(result.custom_message_break_build, "Copacetic patching completed for nginx:latest")
        self.assertEqual(result.scope_pipeline, "")
        self.assertEqual(result.scope_service, "")
        self.assertEqual(result.stage_pipeline, "patch")
        
        # Verify print was called with summary
        mock_print.assert_any_call("==========")
    
    def test_process_missing_image(self):
        """Test process with missing image"""
        # Arrange
        args = {
            "remote_config_repo": "test-repo",
            "remote_config_branch": "main",
            "vulnerability_report": "/path/to/report.json"
        }
        
        # Act
        result = self.copacetic.process(args)
        
        # Assert - The current implementation returns None for exceptions
        self.assertIsNone(result)
    
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
        
        # Assert - The current implementation returns None for failed patches
        self.assertIsNone(result)
    
    def test_process_exception_handling(self):
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
        
        # Assert - The current implementation returns None for exceptions
        self.assertIsNone(result)
    
    @patch('json.dumps')
    @patch('builtins.print')
    def test_summary_printing(self, mock_print, mock_json_dumps):
        """Test that summary is properly printed"""
        # Arrange
        args = {
            "remote_config_repo": "test-repo",
            "remote_config_branch": "main",
            "image": "nginx:latest",
            "vulnerability_report": "/path/to/report.json"
        }
        
        mock_patch_result = {
            "success": True,
            "patched_image": "nginx:latest-patched",
            "vulnerabilities_patched": 3,
            "packages_updated": 2,
            "platforms_processed": ["linux/amd64"],
            "patch_details": ["Updated package1"],
            "output_format": "openvex",
            "output_file": "/path/to/output.json"
        }
        self.copacetic_gateway.patch_image.return_value = mock_patch_result
        self.copacetic_gateway.get_image_info.return_value = {"exists": False}
        
        mock_json_dumps.return_value = "mocked json output"
        
        # Act
        self.copacetic.process(args)
        
        # Assert
        mock_print.assert_any_call("==========")
        mock_print.assert_any_call("mocked json output")
        mock_print.assert_any_call("==========")
        mock_json_dumps.assert_called_once()


if __name__ == '__main__':
    unittest.main()
