import unittest
from unittest.mock import Mock, patch
from devsecops_engine_tools.engine_utilities.copacetic.src.applications.runner_copacetic import runner_copacetic


class TestRunnerCopacetic(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.vulnerability_management_gateway = Mock()
        self.secrets_manager_gateway = Mock()
        self.devops_platform_gateway = Mock()
        self.remote_config_source_gateway = Mock()
        self.metrics_manager_gateway = Mock()
        self.args = {
            "remote_config_repo": "test-repo",
            "remote_config_branch": "main",
            "image": "nginx:latest",
            "vulnerability_report": "/path/to/report.json"
        }
    
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.applications.runner_copacetic.CopaceticAdapter')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.applications.runner_copacetic.init_copacetic')
    def test_runner_copacetic_success(self, mock_init_copacetic, mock_copacetic_adapter):
        """Test successful execution of runner_copacetic"""
        # Arrange
        mock_adapter_instance = Mock()
        mock_copacetic_adapter.return_value = mock_adapter_instance
        
        # Act
        runner_copacetic(
            self.vulnerability_management_gateway,
            self.secrets_manager_gateway,
            self.devops_platform_gateway,
            self.remote_config_source_gateway,
            self.metrics_manager_gateway,
            self.args
        )
        
        # Assert
        mock_copacetic_adapter.assert_called_once()
        mock_init_copacetic.assert_called_once_with(
            vulnerability_management_gateway=self.vulnerability_management_gateway,
            secrets_manager_gateway=self.secrets_manager_gateway,
            devops_platform_gateway=self.devops_platform_gateway,
            remote_config_source_gateway=self.remote_config_source_gateway,
            copacetic_gateway=mock_adapter_instance,
            metrics_manager_gateway=self.metrics_manager_gateway,
            args=self.args
        )
    
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.applications.runner_copacetic.CopaceticAdapter')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.applications.runner_copacetic.init_copacetic')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.applications.runner_copacetic.logger')
    def test_runner_copacetic_exception_handling(self, mock_logger, mock_init_copacetic, mock_copacetic_adapter):
        """Test exception handling in runner_copacetic"""
        # Arrange
        test_exception = Exception("Test exception")
        mock_init_copacetic.side_effect = test_exception
        self.devops_platform_gateway.message.return_value = "error message"
        self.devops_platform_gateway.result_pipeline.return_value = "failed"
        
        # Act
        runner_copacetic(
            self.vulnerability_management_gateway,
            self.secrets_manager_gateway,
            self.devops_platform_gateway,
            self.remote_config_source_gateway,
            self.metrics_manager_gateway,
            self.args
        )
        
        # Assert
        mock_logger.error.assert_called_once_with("Error copacetic: Test exception ")
        self.devops_platform_gateway.message.assert_called_once_with(
            "error", "Error copacetic: Test exception "
        )
        self.devops_platform_gateway.result_pipeline.assert_called_once_with("failed")
    
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.applications.runner_copacetic.CopaceticAdapter')
    def test_copacetic_adapter_initialization(self, mock_copacetic_adapter):
        """Test that CopaceticAdapter is properly initialized"""
        # Arrange
        mock_adapter_instance = Mock()
        mock_copacetic_adapter.return_value = mock_adapter_instance
        
        with patch('devsecops_engine_tools.engine_utilities.copacetic.src.applications.runner_copacetic.init_copacetic'):
            # Act
            runner_copacetic(
                self.vulnerability_management_gateway,
                self.secrets_manager_gateway,
                self.devops_platform_gateway,
                self.remote_config_source_gateway,
                self.metrics_manager_gateway,
                self.args
            )
        
        # Assert
        mock_copacetic_adapter.assert_called_once()


if __name__ == '__main__':
    unittest.main()
