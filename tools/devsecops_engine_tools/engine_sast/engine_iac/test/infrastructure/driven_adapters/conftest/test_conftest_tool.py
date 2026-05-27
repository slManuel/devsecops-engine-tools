import json
import os
import platform
import unittest
from unittest.mock import MagicMock, mock_open, patch

from devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool import (
    ConftestTool,
)


CONFIG_TOOL = {
    "CONFTEST": {
        "VERSION": "0.56.0",
        "POLICY_PATH": "policy",
        "USE_EXTERNAL_CHECKS_DIR": False,
        "EXTERNAL_DIR_OWNER": "",
        "EXTERNAL_DIR_REPOSITORY": "",
        "EXTERNAL_DIR_POLICIES_PATH": "policy",
        "APP_ID_GITHUB": "",
        "INSTALLATION_ID_GITHUB": "",
        "DEFAULT_SEVERITY": "high",
        "DEFAULT_CATEGORY": "vulnerability",
    }
}

CONFIG_TOOL_EXTERNAL = {
    "CONFTEST": {
        "VERSION": "0.56.0",
        "USE_EXTERNAL_CHECKS_DIR": True,
        "EXTERNAL_DIR_OWNER": "my-org",
        "EXTERNAL_DIR_REPOSITORY": "conftest-policies",
        "EXTERNAL_DIR_POLICIES_PATH": "policy",
        "APP_ID_GITHUB": "123",
        "INSTALLATION_ID_GITHUB": "456",
        "DEFAULT_SEVERITY": "high",
        "DEFAULT_CATEGORY": "vulnerability",
    }
}

SAMPLE_RESULTS = [
    {
        "filename": "deploy.yaml",
        "namespace": "main",
        "successes": 1,
        "failures": [
            {
                "msg": "Containers must not run as root",
                "metadata": {"query": "data.main.deny", "id": "CONF_N8N_BC_3"},
            }
        ],
        "warnings": [],
    }
]


class TestConftestTool(unittest.TestCase):
    def setUp(self):
        self.tool = ConftestTool()

    # ------------------------------------------------------------------ #
    # _collect_files                                                       #
    # ------------------------------------------------------------------ #

    @patch("os.path.isfile", return_value=True)
    def test_collect_files_single_file(self, _):
        result = self.tool._collect_files(["deploy.yaml"])
        self.assertEqual(result, ["deploy.yaml"])

    @patch("os.walk", return_value=[("/folder", [], ["a.yaml", "b.tf"])])
    @patch("os.path.isfile", return_value=False)
    @patch("os.path.isdir", return_value=True)
    def test_collect_files_directory(self, _isdir, _isfile, _walk):
        result = self.tool._collect_files(["/folder"])
        self.assertEqual(sorted(result), sorted(["/folder/a.yaml", "/folder/b.tf"]))

    # ------------------------------------------------------------------ #
    # _resolve_policy_path                                                 #
    # ------------------------------------------------------------------ #

    def test_resolve_policy_path_local(self):
        cfg = {"USE_EXTERNAL_CHECKS_DIR": False, "POLICY_PATH": "my_policies"}
        result = self.tool._resolve_policy_path(cfg, None, None, "/tmp")
        self.assertEqual(result, "my_policies")

    def test_resolve_policy_path_local_default(self):
        cfg = {"USE_EXTERNAL_CHECKS_DIR": False}
        result = self.tool._resolve_policy_path(cfg, None, None, "/tmp")
        self.assertEqual(result, "policy")

    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.Utils"
    )
    def test_resolve_policy_path_external_dir(self, mock_utils_cls):
        mock_utils = MagicMock()
        mock_utils_cls.return_value = mock_utils

        cfg = {
            "USE_EXTERNAL_CHECKS_DIR": True,
            "EXTERNAL_DIR_OWNER": "org",
            "EXTERNAL_DIR_REPOSITORY": "repo",
            "EXTERNAL_DIR_POLICIES_PATH": "policy",
            "APP_ID_GITHUB": "1",
            "INSTALLATION_ID_GITHUB": "2",
        }
        result = self.tool._resolve_policy_path(cfg, None, "token:abc", "/tmp")

        mock_utils.configurate_external_checks.assert_called_once_with(
            "CONFTEST",
            {"CONFTEST": cfg},
            None,
            "token:abc",
            agent_work_folder="/tmp",
        )
        self.assertEqual(result, os.path.join("/tmp", "rules", "conftest"))

    @patch("os.path.isdir", return_value=True)
    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.Utils"
    )
    def test_resolve_policy_path_external_custom_subfolder(self, mock_utils_cls, _isdir):
        mock_utils_cls.return_value = MagicMock()
        cfg = {
            "USE_EXTERNAL_CHECKS_DIR": True,
            "EXTERNAL_DIR_POLICIES_PATH": "rego_rules",
        }
        result = self.tool._resolve_policy_path(cfg, None, None, "/workspace")
        self.assertEqual(
            result,
            os.path.join("/workspace", "rules", "conftest", "rego_rules"),
        )

    # ------------------------------------------------------------------ #
    # _install_binary                                                      #
    # ------------------------------------------------------------------ #

    @patch("os.path.isfile", return_value=True)
    def test_install_binary_already_present_linux(self, _):
        result = self.tool._install_binary("0.56.0", "Linux")
        self.assertEqual(result, "./conftest")

    @patch("os.path.isfile", return_value=True)
    def test_install_binary_already_present_windows(self, _):
        result = self.tool._install_binary("0.56.0", "Windows")
        self.assertEqual(result, "./conftest.exe")

    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.requests.get"
    )
    @patch("shutil.which", return_value="/usr/local/bin/conftest")
    @patch("os.path.isfile", return_value=False)
    def test_install_binary_uses_path_before_download(
        self, _isfile, _which, mock_get
    ):
        result = self.tool._install_binary("0.56.0", "Linux")
        self.assertEqual(result, "/usr/local/bin/conftest")
        mock_get.assert_not_called()

    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.logger"
    )
    def test_install_binary_unsupported_platform(self, mock_logger):
        result = self.tool._install_binary("0.56.0", "SunOS")
        self.assertIsNone(result)
        mock_logger.warning.assert_called_once()

    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.Utils"
    )
    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    @patch("builtins.open", new_callable=mock_open)
    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.requests.get"
    )
    @patch("os.path.isfile", return_value=False)
    def test_install_binary_downloads_and_extracts_linux(
        self, _isfile, mock_get, mock_file, mock_subprocess, _which, mock_utils_cls
    ):
        mock_get.return_value = MagicMock(status_code=200, content=b"binary")
        mock_get.return_value.raise_for_status = MagicMock()
        mock_subprocess.return_value = MagicMock(returncode=0)
        mock_utils = MagicMock()
        mock_utils_cls.return_value = mock_utils

        result = self.tool._install_binary("0.56.0", "Linux")
        self.assertEqual(result, "./conftest")
        mock_utils.extract_targz_file.assert_called_once_with(
            "conftest_0.56.0_Linux_x86_64.tar.gz", "."
        )

    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.requests.get",
        side_effect=Exception("network error"),
    )
    @patch("shutil.which", return_value=None)
    @patch("os.path.isfile", return_value=False)
    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.logger"
    )
    def test_install_binary_download_failure(self, mock_logger, _isfile, _which, _get):
        result = self.tool._install_binary("0.56.0", "Linux")
        self.assertIsNone(result)
        mock_logger.error.assert_called_once()

    # ------------------------------------------------------------------ #
    # _execute_conftest                                                    #
    # ------------------------------------------------------------------ #

    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.logger"
    )
    def test_execute_conftest_no_files(self, mock_logger):
        with patch.object(self.tool, "_collect_files", return_value=[]):
            result = self.tool._execute_conftest([], "./conftest", "policy")
        self.assertEqual(result, [])
        mock_logger.warning.assert_called_once()

    @patch("subprocess.run")
    def test_execute_conftest_success(self, mock_subprocess):
        mock_subprocess.return_value = MagicMock(
            stdout=json.dumps(SAMPLE_RESULTS).encode("utf-8")
        )
        with patch.object(self.tool, "_collect_files", return_value=["deploy.yaml"]):
            result = self.tool._execute_conftest(["deploy.yaml"], "./conftest", "policy")
        self.assertEqual(result, SAMPLE_RESULTS)

    @patch("subprocess.run")
    def test_execute_conftest_single_policy_arg(self, mock_subprocess):
        """Verifies a single --policy flag is built from the policy_path string."""
        mock_subprocess.return_value = MagicMock(
            stdout=json.dumps(SAMPLE_RESULTS).encode("utf-8")
        )
        with patch.object(self.tool, "_collect_files", return_value=["deploy.yaml"]):
            self.tool._execute_conftest(
                ["deploy.yaml"], "./conftest", "policy"
            )
        cmd = mock_subprocess.call_args[0][0]
        self.assertEqual(cmd.count("--policy"), 1)
        self.assertIn("policy", cmd)
        self.assertIn("--all-namespaces", cmd)

    @patch("subprocess.run")
    def test_execute_conftest_empty_output(self, mock_subprocess):
        mock_subprocess.return_value = MagicMock(stdout=b"")
        with patch.object(self.tool, "_collect_files", return_value=["deploy.yaml"]):
            result = self.tool._execute_conftest(["deploy.yaml"], "./conftest", "policy")
        self.assertIsNone(result)

    @patch("subprocess.run", side_effect=Exception("subprocess failed"))
    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.logger"
    )
    def test_execute_conftest_exception(self, mock_logger, _):
        with patch.object(self.tool, "_collect_files", return_value=["deploy.yaml"]):
            result = self.tool._execute_conftest(["deploy.yaml"], "./conftest", "policy")
        self.assertIsNone(result)
        mock_logger.error.assert_called_once()

    @patch("subprocess.run")
    def test_execute_conftest_uses_platform_namespace(self, mock_subprocess):
        """Verifies --namespace flag is used per platform instead of --all-namespaces."""
        mock_subprocess.return_value = MagicMock(
            stdout=json.dumps(SAMPLE_RESULTS).encode("utf-8")
        )
        with patch.object(self.tool, "_collect_files", return_value=["workflow.json"]):
            self.tool._execute_conftest(
                ["workflow.json"], "./conftest", "policy", namespaces=["n8n"]
            )
        cmd = mock_subprocess.call_args[0][0]
        self.assertIn("--namespace", cmd)
        self.assertIn("n8n", cmd)
        self.assertNotIn("--all-namespaces", cmd)

    # ------------------------------------------------------------------ #
    # run_tool                                                             #
    # ------------------------------------------------------------------ #

    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.logger"
    )
    def test_run_tool_binary_install_fails(self, _):
        with patch.object(self.tool, "_install_binary", return_value=None):
            findings, path = self.tool.run_tool(CONFIG_TOOL, ["folder"])
        self.assertEqual(findings, [])
        self.assertIsNone(path)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("os.path.abspath", return_value="/tmp/results_conftest.json")
    def test_run_tool_no_results(self, _abspath, _dump, _open):
        with patch.object(self.tool, "_install_binary", return_value="./conftest"):
            with patch.object(self.tool, "_execute_conftest", return_value=[]):
                findings, path = self.tool.run_tool(CONFIG_TOOL, ["folder"])
        self.assertEqual(findings, [])
        self.assertEqual(path, "/tmp/results_conftest.json")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("os.path.abspath", return_value="/tmp/results_conftest.json")
    def test_run_tool_returns_findings_and_path(self, _abspath, _dump, _open):
        with patch.object(self.tool, "_install_binary", return_value="./conftest"):
            with patch.object(
                self.tool, "_execute_conftest", return_value=SAMPLE_RESULTS
            ):
                findings, path = self.tool.run_tool(CONFIG_TOOL, ["folder"])

        self.assertEqual(len(findings), 1)
        self.assertEqual(path, "/tmp/results_conftest.json")

    @patch(
        "devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_tool.Utils"
    )
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("os.path.abspath", return_value="/tmp/results_conftest.json")
    def test_run_tool_uses_external_dir_policies(
        self, _abspath, _dump, _open, mock_utils_cls
    ):
        mock_utils = MagicMock()
        mock_utils_cls.return_value = mock_utils

        with patch.object(self.tool, "_install_binary", return_value="./conftest"):
            with patch.object(
                self.tool, "_execute_conftest", return_value=SAMPLE_RESULTS
            ) as mock_exec:
                findings, path = self.tool.run_tool(
                    CONFIG_TOOL_EXTERNAL,
                    ["folder"],
                    secret_tool=None,
                    secret_external_checks="github_token:abc123",
                    work_folder="/tmp",
                )

        mock_utils.configurate_external_checks.assert_called_once()
        # _execute_conftest receives a string path and no namespaces
        expected_policy_path = os.path.join("/tmp", "rules", "conftest")
        mock_exec.assert_called_once_with(["folder"], "./conftest", expected_policy_path, namespaces=None)
        self.assertEqual(len(findings), 1)

    # ------------------------------------------------------------------ #
    # get_iac_context_from_results                                         #
    # ------------------------------------------------------------------ #

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(SAMPLE_RESULTS),
    )
    def test_get_iac_context_from_results(self, _):
        context_list = self.tool.get_iac_context_from_results("results_conftest.json")
        self.assertEqual(len(context_list), 1)
        ctx = context_list[0]
        self.assertEqual(ctx.id, "CONF_N8N_BC_3")
        self.assertEqual(ctx.tool, "Conftest")
        self.assertEqual(ctx.where, "deploy.yaml")
        self.assertEqual(ctx.check_name, "Containers must not run as root")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps([{"filename": "f.yaml", "failures": None}]),
    )
    def test_get_iac_context_from_results_null_failures(self, _):
        context_list = self.tool.get_iac_context_from_results("results_conftest.json")
        self.assertEqual(context_list, [])


if __name__ == "__main__":
    unittest.main()
