import subprocess
import platform
import os
import requests
import tarfile
import zipfile
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

class TrivyManagerScanUtils():
    def identify_os_and_install(self, trivy_version):
        os_platform = platform.system()
        arch_platform = platform.architecture()[0]
        os_architecture = platform.machine()
        base_url = f"https://github.com/aquasecurity/trivy/releases/download/v{trivy_version}/"

        command_prefix = "trivy"
        
        if os_platform == "Linux":
            if os_architecture == "aarch64":
                file = f"trivy_{trivy_version}_Linux-ARM64.tar.gz"
            else:
                file=f"trivy_{trivy_version}_Linux-{arch_platform}.tar.gz"
            command_prefix = self._install_tool(file, base_url+file, "trivy")
        elif os_platform == "Darwin":
            if os_architecture == "arm64":
                file = f"trivy_{trivy_version}_macOS-ARM64.tar.gz"
            else:
                file=f"trivy_{trivy_version}_macOS-{arch_platform}.tar.gz"
            command_prefix = self._install_tool(file, base_url+file, "trivy")
        elif os_platform == "Windows":
            file=f"trivy_{trivy_version}_windows-{arch_platform}.zip"
            command_prefix = self._install_tool_windows(file, base_url+file, "trivy.exe")
        else:
            logger.warning(f"{os_platform} is not supported.")
            return None

        return command_prefix

    def _install_tool(self, file, url, command_prefix):
        installed = subprocess.run(
            ["which", command_prefix],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if installed.returncode == 1:
            try:
                if not self._download_tool(file, url):
                    return None
                if not tarfile.is_tarfile(file):
                    logger.error(f"Error installing trivy: downloaded file {file} is not a valid tar archive")
                    return None
                with tarfile.open(file, 'r:gz') as tar_file:
                    tar_file.extract(member=tar_file.getmember("trivy"))
                    return "./trivy"
            except Exception as e:
                logger.error(f"Error installing trivy: {e}")
        else:
            return installed.stdout.decode().strip()
        
    def _install_tool_windows(self, file, url, command_prefix):
        try:
            subprocess.run(
                [command_prefix, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return command_prefix
        except:
            try:
                if not self._download_tool(file, url):
                    return None
                if not zipfile.is_zipfile(file):
                    logger.error(f"Error installing trivy: downloaded file {file} is not a valid zip archive")
                    return None
                with zipfile.ZipFile(file, 'r') as zip_file:
                    zip_file.extract(member="trivy.exe")
                    return "./trivy.exe"
            except Exception as e:
                logger.error(f"Error installing trivy: {e}")
    
    def _download_tool(self, file, url):
        try:
            response = requests.get(url, allow_redirects=True, timeout=60)
            response.raise_for_status()
            with open(file, "wb") as compress_file:
                compress_file.write(response.content)
            return True
        except Exception as e:
            if os.path.exists(file):
                os.remove(file)
            logger.error(f"Error downloading trivy: {e}")
            return False

    @staticmethod
    def get_cvss_v3_severity(cvss_score: str, severity: str) -> str:
        if not cvss_score:
            return severity
        else:
            try:
                cvss_score = float(cvss_score)
            except ValueError:
                return severity
            if cvss_score < 4.0:
                return "low"
            elif 4.0 <= cvss_score < 7.0:
                return "medium"
            elif 7.0 <= cvss_score < 9.0:
                return "high"
            elif cvss_score >= 9.0:
                return "critical"
    
    @staticmethod
    def get_cvss_v3_score(cvss_data: any) -> str:
        if not cvss_data:
            return ""
        else:
            return str(
                next(
                    (
                        v["V3Score"]
                        for v in cvss_data.values()
                        if "V3Score" in v
                    ),
                    "",
                )
            )
