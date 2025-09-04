import unittest
from unittest.mock import Mock, patch, MagicMock
from devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic import init_copacetic

class TestEntryPointCopacetic(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.vulnerability_management_gateway = Mock()
        self.secrets_manager_gateway = Mock()
        self.devops_platform_gateway = Mock()
        self.remote_config_source_gateway = Mock()
        self.copacetic_gateway = Mock()
        self.metrics_manager_gateway = Mock()
        
        # Mock devops platform gateway methods
        self.devops_platform_gateway.get_variable.side_effect = lambda var: {
            "pipeline_name": "test-pipeline",
            "branch_tag": "main",
            "stage": "patch"
        }.get(var, "")
        
        self.args = {
            "remote_config_repo": "test-repo",
            "remote_config_branch": "main",
            "send_metrics": "true",
            "image": "nginx:latest"
        }
        
        # Mock configurations
        self.config_tool = {
            "COPACETIC": {
                "ENABLED": True
            }
        }
        
        self.copacetic_config_tool = {
            "IGNORE_SEARCH_PATTERN": "^ignore-.*",
            "TARGET_BRANCHES": ["main", "develop", "release"]
        }
        
        self.excluded_pipelines = {
            "excluded-pipeline": True,
            "BY_PATTERN_SEARCH": {
                "ignore-.*": True
            }
        }
        
        # Setup remote config gateway
        def get_remote_config_side_effect(repo, path, branch):
            if "ConfigTool.json" in path and "engine_core" in path:
                return self.config_tool
            elif "ConfigTool.json" in path and "copacetic" in path:
                return self.copacetic_config_tool
            elif "Exclusions.json" in path:
                return self.excluded_pipelines
            return {}
        
        self.remote_config_source_gateway.get_remote_config.side_effect = get_remote_config_side_effect
        
        # Setup devops platform gateway
        self.devops_platform_gateway.get_variable.side_effect = lambda var: {
            "pipeline_name": "test-pipeline",
            "branch_tag": "main"
        }.get(var, "")
    
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.logger')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.Copacetic')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.MetricsManager')
    def test_init_copacetic_enabled_valid_pipeline_valid_branch(self, mock_metrics_manager, mock_copacetic, mock_logger):
        """Test init_copacetic when enabled with valid pipeline and branch"""
        # Arrange
        mock_copacetic_instance = Mock()
        mock_input_core = Mock()
        mock_input_core.stage_pipeline = "patch"  # Add the missing attribute
        mock_copacetic_instance.process.return_value = mock_input_core
        mock_copacetic.return_value = mock_copacetic_instance
        
        mock_metrics_instance = Mock()
        mock_metrics_manager.return_value = mock_metrics_instance
        
        # Act
        init_copacetic(
            self.vulnerability_management_gateway,
            self.secrets_manager_gateway,
            self.devops_platform_gateway,
            self.remote_config_source_gateway,
            self.copacetic_gateway,
            self.metrics_manager_gateway,
            self.args
        )
        
        # Assert
        mock_copacetic.assert_called_once_with(
            self.vulnerability_management_gateway,
            self.secrets_manager_gateway,
            self.devops_platform_gateway,
            self.remote_config_source_gateway,
            self.copacetic_gateway
        )
        mock_copacetic_instance.process.assert_called_once_with(self.args)
        mock_metrics_manager.assert_called_once()
        mock_metrics_instance.process.assert_called_once()
    
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.Copacetic')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.logger')
    def test_init_copacetic_disabled(self, mock_logger, mock_copacetic):
        """Test init_copacetic when disabled"""
        # Arrange
        self.config_tool["COPACETIC"]["ENABLED"] = False
        self.devops_platform_gateway.message.return_value = "warning message"
        
        # Act
        init_copacetic(
            self.vulnerability_management_gateway,
            self.secrets_manager_gateway,
            self.devops_platform_gateway,
            self.remote_config_source_gateway,
            self.copacetic_gateway,
            self.metrics_manager_gateway,
            self.args
        )
        
        # Assert
        mock_copacetic.assert_not_called()
        self.devops_platform_gateway.message.assert_called_once_with(
            "warning", "DevSecOps Engine Tool - copacetic in maintenance..."
        )
    
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.Copacetic')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.logger')
    def test_init_copacetic_excluded_pipeline(self, mock_logger, mock_copacetic):
        """Test init_copacetic with excluded pipeline"""
        # Arrange
        self.devops_platform_gateway.get_variable.side_effect = lambda var: {
            "pipeline_name": "excluded-pipeline",
            "branch_tag": "main"
        }.get(var, "")
        self.devops_platform_gateway.message.return_value = "warning message"
        
        # Act
        init_copacetic(
            self.vulnerability_management_gateway,
            self.secrets_manager_gateway,
            self.devops_platform_gateway,
            self.remote_config_source_gateway,
            self.copacetic_gateway,
            self.metrics_manager_gateway,
            self.args
        )
        
        # Assert
        mock_copacetic.assert_not_called()
        self.devops_platform_gateway.message.assert_called_once_with(
            "warning", "Tool skipped by DevSecOps policy"
        )
    
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.Copacetic')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.logger')
    def test_init_copacetic_invalid_branch(self, mock_logger, mock_copacetic):
        """Test init_copacetic with invalid branch"""
        # Arrange
        self.devops_platform_gateway.get_variable.side_effect = lambda var: {
            "pipeline_name": "valid-pipeline",
            "branch_tag": "feature/invalid"
        }.get(var, "")
        self.devops_platform_gateway.message.return_value = "warning message"
        
        # Act
        init_copacetic(
            self.vulnerability_management_gateway,
            self.secrets_manager_gateway,
            self.devops_platform_gateway,
            self.remote_config_source_gateway,
            self.copacetic_gateway,
            self.metrics_manager_gateway,
            self.args
        )
        
        # Assert
        mock_copacetic.assert_not_called()
        self.devops_platform_gateway.message.assert_called_once_with(
            "warning", "Tool skipped by DevSecOps policy"
        )
    
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.logger')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.Copacetic')
    def test_init_copacetic_pattern_exclusion(self, mock_copacetic, mock_logger):
        """Test init_copacetic with pattern-based exclusion"""
        # Arrange
        self.devops_platform_gateway.get_variable.side_effect = lambda var: {
            "pipeline_name": "ignore-test-pipeline",
            "branch_tag": "main"
        }.get(var, "")
        
        # Act
        init_copacetic(
            self.vulnerability_management_gateway,
            self.secrets_manager_gateway,
            self.devops_platform_gateway,
            self.remote_config_source_gateway,
            self.copacetic_gateway,
            self.metrics_manager_gateway,
            self.args
        )
        
        # Assert
        mock_copacetic.assert_not_called()
    
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.logger')
    @patch('devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic.Copacetic')
    def test_init_copacetic_no_metrics(self, mock_copacetic, mock_logger):
        """Test init_copacetic without sending metrics"""
        # Arrange
        self.args["send_metrics"] = "false"
        mock_copacetic_instance = Mock()
        mock_input_core = Mock()
        mock_copacetic_instance.process.return_value = mock_input_core
        mock_copacetic.return_value = mock_copacetic_instance
        
        # Act
        init_copacetic(
            self.vulnerability_management_gateway,
            self.secrets_manager_gateway,
            self.devops_platform_gateway,
            self.remote_config_source_gateway,
            self.copacetic_gateway,
            self.metrics_manager_gateway,
            self.args
        )
        
        # Assert
        mock_copacetic.assert_called_once()
        mock_copacetic_instance.process.assert_called_once_with(self.args)
