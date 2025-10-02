import platform
import stat
import requests
import os
import glob
import subprocess
import logging
import re
import base64
import traceback
from devsecops_engine_tools.engine_sca.engine_function.src.domain.model.gateways.tool_gateway import (
    ToolGateway,
)
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings



logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


class PrismaCloudManagerScan:
    def __init__(
        self,
        tool_run: ToolGateway,
        dict_args
    ):
        self.tool_run = tool_run
        self.dict_args = dict_args

    def run_tool_function_sca(
        self, 
        remoteconfig, 
        secret_tool,
        token_engine_container,
        skip_flag,
    ):
        prisma_key = (
            f"{secret_tool['access_prisma']}:{secret_tool['token_prisma']}" if secret_tool else token_engine_container
        )
        if not (skip_flag):
            try:
                file_path = os.path.join(
                    os.getcwd(), remoteconfig["PRISMA_CLOUD"]["TWISTCLI_PATH"]
                )
                if not os.path.exists(file_path):
                    self._download_twistcli(
                        file_path,
                        remoteconfig["PRISMA_CLOUD"]["PRISMA_ACCESS_KEY"],
                        prisma_key,
                        remoteconfig["PRISMA_CLOUD"]["PRISMA_CONSOLE_URL"],
                        remoteconfig["PRISMA_CLOUD"]["PRISMA_API_VERSION"],
                    )
                folder_path = self.dict_args["folder_path"]
                function_scan = self._scan_function(
                    file_path,
                    folder_path,
                    remoteconfig,
                    prisma_key,
                )

                return function_scan

            except Exception as ex:
                traceback.print_exc()
                logger.error(f"An overall error occurred: {ex}")
        else:
            print('##[info] Skipping function scan')
            return 0

    def download_twistcli(
        self,
        file_path,
        prisma_key,
        prisma_console_url,
        prisma_api_version,
    ):
        
        machine = platform.machine()
        system = platform.system()

        base_url = f"{prisma_console_url}/api/{prisma_api_version}/util"

        os_mapping = {
            "Linux": "twistcli",
            "Windows": "windows/twistcli.exe",
            "Darwin": "osx/twistcli",
        }

        url = f"{base_url}/{os_mapping[system]}"

        if system == "Linux" and machine == "aarch64":
            url = f"{base_url}/arm64/twistcli"
        elif system == "Darwin" and machine == "aarch64":
            url = f"{base_url}/osx/arm64/twistcli"

        credentials = base64.b64encode(
            prisma_key.encode()
        ).decode()
        headers = {"Authorization": f"Basic {credentials}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            with open(file_path, "wb") as file:
                file.write(response.content)

            os.chmod(file_path, stat.S_IRWXU)
            logger.info(f"twistcli downloaded and saved to: {file_path}")
            return 0

        except Exception as e:
            raise ValueError(f"Error downloading twistcli: {e}")
        
    def _scan_function(self, file_path, folder_path, remoteconfig, prisma_key):
        function_path = glob.glob(os.path.join(folder_path, "*.zip"))
        if not function_path:
            print("##vso[task.logissue type=warning;code=100;] No .zip file found [Scanning skipped]")
            return None
        zip_name = os.path.basename(function_path[0])
        command = (
            file_path,
            "serverless",
            "scan",
            "--address",
            remoteconfig["PRISMA_CLOUD"]["PRISMA_CONSOLE_URL"],
            "--user",
            remoteconfig["PRISMA_CLOUD"]["PRISMA_ACCESS_KEY"],
            "--password",
            prisma_key,
            "--details",
            function_path[0],
        )
        try:
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                errors="replace"
            )
            print(f"The function {zip_name} was scanned")
            result = self._parse_scan_results(result.stdout)
            return result

        except subprocess.CalledProcessError as e:
            logger.error(
                f"Error during function scan of {zip_name}"
                f"\n errorcode: {e.returncode}"
                f"\n output: {e.output}"
            )

    def _parse_scan_results(self, stdout: str) -> dict:
        def extract_dist(pattern: str) -> dict:
            match = re.search(pattern, stdout)
            return {
                "critical": int(match.group(2)),
                "high": int(match.group(3)),
                "medium": int(match.group(4)),
                "low": int(match.group(5)),
                "total": int(match.group(1))
            } if match else {}

        def clean_text(text) -> str:
            cleaned_text = text.replace('\x1b[0m', '')
            cleaned_text = cleaned_text.replace('\x1b[91;1m', '')
            return cleaned_text

        def extract_table() -> list:
            lines = stdout.splitlines()
            table_start = [i for i, line in enumerate(lines) if 'CVE-' in line]
            table_data = []
            if table_start:
                i = table_start[0]
                while i < len(lines):
                    if "CVE-" in lines[i]:
                        row = lines[i]
                        desc_lines = []
                        i += 1
                        while i < len(lines) and not lines[i].strip().startswith("| CVE-") and not "+---" in lines[i]:
                            desc_lines.append(lines[i])
                            i += 1
                        full_row = row + "\n" + "\n".join(desc_lines)
                        table_data.append(full_row)
                    else:
                        i += 1

            vulnerabilities = []
            for row in table_data:
                parts = [x.strip() for x in row.split("|")[1:-1]]
                if len(parts) >= 9:
                    vuln = {
                        "id": clean_text(parts[0]),
                        "severity": clean_text(parts[1]),
                        "cvss": float(clean_text(parts[2])) if parts[2] else 0.0,
                        "packageName": clean_text(parts[3]),
                        "packageVersion": clean_text(parts[4]),
                        "status": clean_text(parts[5]),
                        "publishedDate": clean_text(parts[6]),
                        "discoveredDate": clean_text(parts[7]),
                        "description": clean_text(parts[8]).replace("u00a0", " ").strip(" .") + "..."
                    }
                    vulnerabilities.append(vuln)
            return vulnerabilities

        name_match = re.search(r"Scan results for: function (.+?)\s", stdout)
        function_name = name_match.group(1) if name_match else "unknown.zip"

        return {
            "results": [
                {
                    "name": function_name,
                    "complianceDistribution": extract_dist(r"Compliance found for function .*?: total - (\d+), critical - (\d+), high - (\d+), medium - (\d+), low - (\d+)"),
                    "complianceScanPassed": "Compliance threshold check results: PASS" in stdout,
                    "vulnerabilities": extract_table(),
                    "vulnerabilityDistribution": extract_dist(r"Vulnerabilities found for function .*?: total - (\d+), critical - (\d+), high - (\d+), medium - (\d+), low - (\d+)"),
                    "vulnerabilityScanPassed": "Vulnerability threshold check results: PASS" in stdout
                }
            ]
        }
