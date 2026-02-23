import os
import json
import unittest
from unittest.mock import patch, mock_open

from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.runtime_local.runtime_local import (
    RuntimeLocal,
)


class TestRuntimeLocal(unittest.TestCase):

    def setUp(self):
        self.runtime = RuntimeLocal()

    # ------------------------------------------------------------------ #
    # get_remote_config                                                    #
    # ------------------------------------------------------------------ #

    def test_get_remote_config(self):
        config_data = {"key": "value"}
        json_content = json.dumps(config_data)
        with patch("builtins.open", mock_open(read_data=json_content)):
            result = self.runtime.get_remote_config("my_repo", "path/to/config.json")
        self.assertEqual(result, config_data)

    # ------------------------------------------------------------------ #
    # message                                                              #
    # ------------------------------------------------------------------ #

    def test_message_succeeded(self):
        result = self.runtime.message("succeeded", "OK")
        self.assertEqual(result, f"{self.runtime.OKGREEN}OK{self.runtime.ENDC}")

    def test_message_info(self):
        result = self.runtime.message("info", "Info msg")
        self.assertEqual(result, f"{self.runtime.BOLD}Info msg{self.runtime.ENDC}")

    def test_message_warning(self):
        result = self.runtime.message("warning", "Warn msg")
        self.assertEqual(result, f"{self.runtime.WARNING}Warn msg{self.runtime.ENDC}")

    def test_message_error(self):
        result = self.runtime.message("error", "Err msg")
        self.assertEqual(result, f"{self.runtime.FAIL}Err msg{self.runtime.ENDC}")

    # ------------------------------------------------------------------ #
    # result_pipeline                                                      #
    # ------------------------------------------------------------------ #

    def test_result_pipeline_failed(self):
        result = self.runtime.result_pipeline("failed")
        self.assertEqual(
            result,
            f"{self.runtime.FAIL}{self.runtime.ICON_FAIL}Failed{self.runtime.ENDC}",
        )

    def test_result_pipeline_succeeded(self):
        result = self.runtime.result_pipeline("succeeded")
        self.assertEqual(
            result,
            f"{self.runtime.OKGREEN}{self.runtime.ICON_SUCCESS}Succeeded{self.runtime.ENDC}",
        )

    def test_result_pipeline_succeeded_with_issues(self):
        result = self.runtime.result_pipeline("succeeded_with_issues")
        self.assertEqual(
            result,
            f"{self.runtime.WARNING}{self.runtime.ICON_SUCCESS}Succeeded with issues{self.runtime.ENDC}",
        )

    # ------------------------------------------------------------------ #
    # get_source_code_management_uri                                       #
    # ------------------------------------------------------------------ #

    def test_get_source_code_management_uri(self):
        with patch.dict(os.environ, {"DET_SOURCE_CODE_MANAGEMENT_URI": "https://github.com/org/repo"}):
            result = self.runtime.get_source_code_management_uri()
        self.assertEqual(result, "https://github.com/org/repo")

    def test_get_source_code_management_uri_not_set(self):
        env = {k: v for k, v in os.environ.items() if k != "DET_SOURCE_CODE_MANAGEMENT_URI"}
        with patch.dict(os.environ, env, clear=True):
            result = self.runtime.get_source_code_management_uri()
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    # get_build_pipeline_execution_url                                     #
    # ------------------------------------------------------------------ #

    def test_get_build_pipeline_execution_url(self):
        with patch.dict(os.environ, {"DET_BUILD_PIPELINE_EXECUTION_URL": "https://ci.example.com/build/42"}):
            result = self.runtime.get_build_pipeline_execution_url()
        self.assertEqual(result, "https://ci.example.com/build/42")

    def test_get_build_pipeline_execution_url_not_set(self):
        env = {k: v for k, v in os.environ.items() if k != "DET_BUILD_PIPELINE_EXECUTION_URL"}
        with patch.dict(os.environ, env, clear=True):
            result = self.runtime.get_build_pipeline_execution_url()
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    # get_variable                                                         #
    # ------------------------------------------------------------------ #

    def test_get_variable_branch_name(self):
        with patch.dict(os.environ, {"DET_BRANCH_NAME": "main"}):
            result = self.runtime.get_variable("branch_name")
        self.assertEqual(result, "main")

    def test_get_variable_build_id(self):
        with patch.dict(os.environ, {"DET_BUILD_ID": "123"}):
            result = self.runtime.get_variable("build_id")
        self.assertEqual(result, "123")

    def test_get_variable_commit_hash(self):
        with patch.dict(os.environ, {"DET_COMMIT_HASH": "abc123def"}):
            result = self.runtime.get_variable("commit_hash")
        self.assertEqual(result, "abc123def")

    def test_get_variable_environment(self):
        with patch.dict(os.environ, {"DET_ENVIRONMENT": "production"}):
            result = self.runtime.get_variable("environment")
        self.assertEqual(result, "production")

    def test_get_variable_repository(self):
        with patch.dict(os.environ, {"DET_REPOSITORY": "my-repo"}):
            result = self.runtime.get_variable("repository")
        self.assertEqual(result, "my-repo")

    def test_get_variable_returns_none_when_not_set(self):
        env = {k: v for k, v in os.environ.items() if k != "DET_BRANCH_NAME"}
        with patch.dict(os.environ, env, clear=True):
            result = self.runtime.get_variable("branch_name")
        self.assertIsNone(result)

    def test_get_variable_build_task(self):
        with patch.dict(os.environ, {"DET_APPLICATION_BUILD_TASK": "build_task_value"}):
            result = self.runtime.get_variable("build_task")
        self.assertEqual(result, "build_task_value")

    # ------------------------------------------------------------------ #
    # set_variable                                                         #
    # ------------------------------------------------------------------ #

    def test_set_variable(self):
        with patch.dict(os.environ, {}, clear=False):
            self.runtime.set_variable("MY_TEST_VAR", "test_value")
            self.assertEqual(os.environ.get("MY_TEST_VAR"), "test_value")


if __name__ == "__main__":
    unittest.main()
