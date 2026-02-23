import unittest
from unittest.mock import MagicMock
from unittest import mock
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions import GithubActions
from tools.devsecops_engine_tools.engine_utilities.github.models import GithubPredefinedVariables

class TestGithubActions(unittest.TestCase):

    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.GithubApi',
        autospec=True
    )
    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.SystemVariables',
        autospec=True
    )
    def test_get_remote_config(self, mock_system_variables, mock_github_api):
        github_actions = GithubActions()

        # Set up mock values for SystemVariables
        mock_system_variables.github_repository.value.return_value = "github_repository"

        # Mock the AzureDevopsApi class
        mock_github_api_instance = MagicMock()
        mock_github_api_instance.get_azure_connection.return_value = "MockedConnection"
        mock_github_api_instance.get_remote_json_config.return_value = {'key': 'value'}
        mock_github_api.return_value = mock_github_api_instance

        remote_config_repo = "my_repo"
        remote_config_path = "my_path"
        result = github_actions.get_remote_config(remote_config_repo, remote_config_path)

        assert result == {"key": "value"}

    def test_message(self):

        github_actions = GithubActions()

        assert github_actions.message("succeeded", "message") == "::group::message"
        assert github_actions.message("info", "message") == "::notice::message"
        assert github_actions.message("warning", "message") == "::warning::message"
        assert github_actions.message("error", "message") == "::error::message"

    def test_result_pipeline(self):
        ENDC = "\033[0m"
        FAIL = "\033[91m"
        OKGREEN = "\033[92m"
        ICON_FAIL = "\u2718"
        ICON_SUCCESS = "\u2714"

        github_actions = GithubActions()

        assert github_actions.result_pipeline("failed") == f"{FAIL}{ICON_FAIL}Failed{ENDC}"
        assert github_actions.result_pipeline("succeeded") == f"{OKGREEN}{ICON_SUCCESS}Succeeded{ENDC}"

    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.SystemVariables',
        autospec=True)
    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.BuildVariables',
        autospec=True)
    def test_get_build_pipeline_execution_url(self,mock_build_variables, mock_system_variables):
        github_actions = GithubActions()

        # Mock the BuildVariables class
        mock_build_variables.github_run_id.value.return_value = "github_run_id"

        # Mock the SystemVariables class
        mock_system_variables.github_server_url.value.return_value = "github_server_url"
        mock_system_variables.github_repository.value.return_value = "github_repository"

        assert github_actions.get_build_pipeline_execution_url() == "github_server_url/github_repository/actions/runs/github_run_id"

    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.SystemVariables',
        autospec=True)
    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.BuildVariables',
        autospec=True)
    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.ReleaseVariables',
        autospec=True)
    def test_get_variable(self, mock_release_variables, mock_build_variables, mock_system_variables):
        github_actions = GithubActions()

        # Mock the BuildVariables class
        mock_build_variables.github_ref.value.return_value = "github_ref"
        mock_build_variables.github_run_number.value.return_value = "github_run_number"
        mock_build_variables.github_run_id.value.return_value = "github_run_id"
        mock_build_variables.github_sha.value.return_value = "github_sha"
        

        # Mock the ReleaseVariables class
        mock_release_variables.github_workflow.value.return_value = "github_workflow"
        mock_release_variables.github_env.value.return_value = "github_env"
        mock_release_variables.github_run_number.value.return_value = "github_run_number"

        # Mock the SystemVariables class
        mock_system_variables.github_access_token.value.return_value = "github_access_token"

        result = github_actions.get_variable("branch_name")
        assert result == "github_ref"

        result = github_actions.get_variable("build_id")
        assert result == "github_run_number"

        result = github_actions.get_variable("build_execution_id")
        assert result == "github_run_id"

        result = github_actions.get_variable("commit_hash")
        assert result == "github_sha"

        result = github_actions.get_variable("environment")
        assert result == "github_env"

        result = github_actions.get_variable("release_id")
        assert result == "github_run_number"

        result = github_actions.get_variable("branch_tag")
        assert result == "github_ref"

        result = github_actions.get_variable("access_token")
        assert result == "github_access_token"


class TestEnvVariables(unittest.TestCase):
    @mock.patch('os.environ.get')
    def test_get_value_variable_exists(self, mock_env_get):
        # Arrange
        mock_env_get.return_value = "test_value"
        
        # Act
        result = GithubPredefinedVariables.EnvVariables.get_value("TEST_VARIABLE")
        
        # Assert
        self.assertEqual(result, "test_value")
        mock_env_get.assert_called_once_with("TEST_VARIABLE")

    @mock.patch('os.environ.get')
    def test_get_value_variable_not_exists(self, mock_env_get):
        # Arrange
        mock_env_get.return_value = None
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            GithubPredefinedVariables.EnvVariables.get_value("TEST_VARIABLE")
        self.assertEqual(str(context.exception), "La variable de entorno TEST_VARIABLE no está definida")
        mock_env_get.assert_called_once_with("TEST_VARIABLE")

    @mock.patch('os.environ.get')
    def test_get_value_custom_repository_name_none(self, mock_env_get):
        # Arrange
        mock_env_get.return_value = None
        
        # Act
        result = GithubPredefinedVariables.EnvVariables.get_value("CUSTOM_REPOSITORY_NAME")
        
        # Assert
        self.assertIsNone(result)
        mock_env_get.assert_called_once_with("CUSTOM_REPOSITORY_NAME")

    @mock.patch('os.environ.get')
    def test_get_value_custom_pipeline_name_none(self, mock_env_get):
        # Arrange
        mock_env_get.return_value = None
        
        # Act
        result = GithubPredefinedVariables.EnvVariables.get_value("CUSTOM_PIPELINE_NAME")
        
        # Assert
        self.assertIsNone(result)
        mock_env_get.assert_called_once_with("CUSTOM_PIPELINE_NAME")

    @mock.patch('os.environ.get')
    def test_get_value_custom_repository_name_exists(self, mock_env_get):
        # Arrange
        mock_env_get.return_value = "repo_name"
        
        # Act
        result = GithubPredefinedVariables.EnvVariables.get_value("CUSTOM_REPOSITORY_NAME")
        
        # Assert
        self.assertEqual(result, "repo_name")
        mock_env_get.assert_called_once_with("CUSTOM_REPOSITORY_NAME")

    @mock.patch('os.environ.get')
    def test_get_value_custom_pipeline_name_exists(self, mock_env_get):
        # Arrange
        mock_env_get.return_value = "pipeline_name"
        
        # Act
        result = GithubPredefinedVariables.EnvVariables.get_value("CUSTOM_PIPELINE_NAME")
        
        # Assert
        self.assertEqual(result, "pipeline_name")
        mock_env_get.assert_called_once_with("CUSTOM_PIPELINE_NAME")


class TestGithubActionsAdditional(unittest.TestCase):

    def test_result_pipeline_succeeded_with_issues(self):
        WARNING = "\033[93m"
        ENDC = "\033[0m"
        ICON_SUCCESS = "\u2714"
        github_actions = GithubActions()
        result = github_actions.result_pipeline("succeeded_with_issues")
        self.assertEqual(result, f"{WARNING}{ICON_SUCCESS}Succeeded with issues{ENDC}")

    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.SystemVariables',
        autospec=True)
    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.BuildVariables',
        autospec=True)
    def test_get_source_code_management_uri(self, mock_build_variables, mock_system_variables):
        github_actions = GithubActions()
        mock_system_variables.github_server_url.value.return_value = "https://github.com"
        mock_build_variables.github_repository.value.return_value = "octocat/hello-world"
        result = github_actions.get_source_code_management_uri()
        self.assertEqual(result, "https://github.com/octocat/hello-world")

    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.SystemVariables',
        autospec=True)
    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.BuildVariables',
        autospec=True)
    @mock.patch(
        'devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions.ReleaseVariables',
        autospec=True)
    def test_get_variable_value_error_returns_none(self, mock_release_variables, mock_build_variables, mock_system_variables):
        github_actions = GithubActions()
        mock_build_variables.github_ref.value.side_effect = ValueError("not defined")
        result = github_actions.get_variable("branch_name")
        self.assertIsNone(result)

    def test_set_variable(self):
        github_actions = GithubActions()
        with mock.patch('builtins.print') as mock_print:
            github_actions.set_variable("MY_VAR", "my_value")
            mock_print.assert_called_once_with("::set-output name=MY_VAR::my_value")


if __name__ == '__main__':
    unittest.main()