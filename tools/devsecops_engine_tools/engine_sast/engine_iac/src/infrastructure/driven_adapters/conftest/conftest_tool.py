import subprocess
import json
import platform
import requests
import os
import shutil
from typing import List

from devsecops_engine_tools.engine_sast.engine_iac.src.domain.model.context_iac import (
    ContextIac,
)
from devsecops_engine_tools.engine_sast.engine_iac.src.domain.model.gateways.tool_gateway import (
    ToolGateway,
)
from devsecops_engine_tools.engine_sast.engine_iac.src.infrastructure.driven_adapters.conftest.conftest_deserealizator import (
    ConftestDeserealizator,
)
from devsecops_engine_tools.engine_utilities.utils.utils import Utils
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

PLATFORM_BINARY_MAP = {
    "Linux": ("conftest_{version}_Linux_x86_64.tar.gz", "conftest"),
    "Darwin": ("conftest_{version}_Darwin_x86_64.tar.gz", "conftest"),
    "Windows": ("conftest_{version}_Windows_x86_64.zip", "conftest.exe"),
}


class ConftestTool(ToolGateway):
    TOOL_CONFTEST = "CONFTEST"
    RESULTS_FILE = "results_conftest.json"

    def run_tool(self, config_tool, folders_to_scan, **kwargs):
        conftest_config = config_tool.get(self.TOOL_CONFTEST, {})
        version = conftest_config.get("VERSION")
        default_severity = conftest_config.get("DEFAULT_SEVERITY", "low")
        default_category = conftest_config.get("DEFAULT_CATEGORY", "vulnerability")

        secret_tool = kwargs.get("secret_tool")
        secret_external_checks = kwargs.get("secret_external_checks")
        work_folder = kwargs.get("work_folder")
        platform_to_scan = kwargs.get("platform_to_scan") or None

        policy_path = self._resolve_policy_path(
            conftest_config, secret_tool, secret_external_checks, work_folder
        )

        os_platform = platform.system()
        command_prefix = self._install_binary(version, os_platform)

        if command_prefix is None:
            return [], None

        results = self._execute_conftest(folders_to_scan, command_prefix, policy_path, namespaces=platform_to_scan)

        if results is None:
            return [], None

        results_path = os.path.abspath(self.RESULTS_FILE)
        with open(results_path, "w") as f:
            json.dump(results, f, indent=4)

        deserealizator = ConftestDeserealizator()
        findings_list = deserealizator.get_list_finding(
            results, default_severity, default_category,
            rules_config=conftest_config.get("RULES", {})
        )

        return findings_list, results_path

    def _resolve_policy_path(
        self, conftest_config, secret_tool, secret_external_checks, work_folder
    ):
        if conftest_config.get("USE_EXTERNAL_CHECKS_DIR", False):
            util = Utils()
            util.configurate_external_checks(
                self.TOOL_CONFTEST,
                {self.TOOL_CONFTEST: conftest_config},
                secret_tool,
                secret_external_checks,
                agent_work_folder=work_folder,
            )
            base_policies_path = os.path.join(work_folder, "rules", "conftest")
            policies_subfolder = conftest_config.get(
                "EXTERNAL_DIR_POLICIES_PATH", ""
            ).strip("/\\")

            if policies_subfolder:
                candidate_path = os.path.join(base_policies_path, policies_subfolder)
                if os.path.isdir(candidate_path):
                    return candidate_path

            return base_policies_path

        return conftest_config.get("POLICY_PATH", "policy")

    def get_iac_context_from_results(self, path_file_results: str) -> List[ContextIac]:
        with open(path_file_results, "r") as f:
            results = json.load(f)

        context_list = []
        for file_result in results:
            filename = file_result.get("filename", "unknown")
            for failure in file_result.get("failures", []) or []:
                msg = failure.get("msg", "unknown")
                metadata = failure.get("metadata", {}) or {}
                finding_id = metadata.get("id") or metadata.get("query", "unknown")
                severity = metadata.get("severity", "medium").lower()

                context_iac = ContextIac(
                    id=finding_id,
                    check_name=msg,
                    check_class="conftest",
                    severity=severity,
                    where=filename,
                    resource=filename,
                    description=msg,
                    module="engine_iac",
                    tool="Conftest",
                )
                context_list.append(context_iac)

        return context_list

    def _install_binary(self, version: str, os_platform: str) -> str:
        if os_platform not in PLATFORM_BINARY_MAP:
            logger.warning(f"Unsupported platform for conftest: {os_platform}")
            return None

        filename_template, binary_name = PLATFORM_BINARY_MAP[os_platform]
        filename = filename_template.format(version=version)

        if os.path.isfile(binary_name):
            logger.info(f"Conftest binary already present: {binary_name}")
            return f"./{binary_name}"

        binary_in_path = shutil.which(binary_name) or shutil.which("conftest")
        if binary_in_path:
            logger.info(f"Conftest binary found in PATH: {binary_in_path}")
            return binary_in_path

        base_url = (
            f"https://github.com/open-policy-agent/conftest/releases/download/v{version}/"
        )
        url = base_url + filename

        try:
            logger.info(f"Downloading conftest from {url}")
            response = requests.get(url, allow_redirects=True, timeout=60)
            response.raise_for_status()

            with open(filename, "wb") as f:
                f.write(response.content)

            if filename.endswith(".tar.gz"):
                Utils().extract_targz_file(filename, ".")
            elif filename.endswith(".zip"):
                Utils().unzip_file(filename, ".")

            if os_platform != "Windows":
                subprocess.run(["chmod", "+x", binary_name], check=True)

            return f"./{binary_name}"

        except Exception as e:
            logger.error(f"Error installing conftest: {e}")
            return None

    def _execute_conftest(
        self, folders_to_scan: list, command_prefix: str, policy_path: str, namespaces=None
    ):
        files_to_test = self._collect_files(folders_to_scan)

        if not files_to_test:
            logger.warning("No files found to scan with conftest")
            return []

        if namespaces:
            namespace_args = []
            for ns in namespaces:
                namespace_args += ["--namespace", ns]
        else:
            namespace_args = ["--all-namespaces"]

        command = (
            [command_prefix, "test"]
            + files_to_test
            + ["--policy", policy_path]
            + namespace_args
            + ["--output", "json", "--no-fail"]
        )

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output = result.stdout.decode("utf-8").strip()
            if not output:
                logger.warning("Conftest returned empty output")
                return None
            return json.loads(output)
        except Exception as e:
            logger.error(f"Error executing conftest: {e}")
            return None

    def _collect_files(self, folders_to_scan: list) -> list:
        files = []
        for path in folders_to_scan:
            if os.path.isfile(path):
                files.append(path)
            elif os.path.isdir(path):
                for root, _, filenames in os.walk(path):
                    for fname in filenames:
                        files.append(os.path.join(root, fname))
        return files
