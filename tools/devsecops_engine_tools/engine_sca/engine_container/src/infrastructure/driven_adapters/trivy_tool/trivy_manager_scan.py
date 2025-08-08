from devsecops_engine_tools.engine_sca.engine_container.src.domain.model.gateways.tool_gateway import (
    ToolGateway,
)

import subprocess
import platform
import requests
import tarfile
import zipfile
import json

from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

from devsecops_engine_tools.engine_utilities.sbom.deserealizator import (
    get_list_component,
)

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


class TrivyScan(ToolGateway):
    def download_tool(self, file, url):
        try:
            response = requests.get(url, allow_redirects=True)
            with open(file, "wb") as compress_file:
                compress_file.write(response.content)
        except Exception as e:
            logger.error(f"Error downloading trivy: {e}")

    def install_tool(self, file, url, command_prefix):
        installed = subprocess.run(
            ["which", command_prefix],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if installed.returncode == 1:
            try:
                self.download_tool(file, url)
                with tarfile.open(file, 'r:gz') as tar_file:
                    tar_file.extract(member=tar_file.getmember("trivy"))
                    return "./trivy"
            except Exception as e:
                logger.error(f"Error installing trivy: {e}")
        else:
            return installed.stdout.decode().strip()
        
    def install_tool_windows(self, file, url, command_prefix):
        try:
            subprocess.run(
                [command_prefix, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return command_prefix
        except:
            try:
                self.download_tool(file, url)
                with zipfile.ZipFile(file, 'r') as zip_file:
                    zip_file.extract(member="trivy.exe")
                    return "./trivy.exe"
            except Exception as e:
                logger.error(f"Error installing trivy: {e}")

    def scan_image(self, prefix, image_name, result_file, base_image, is_compressed_file=False):
        command = [
            prefix,
            "--scanners",
            "vuln",
            "-f",
            "json",
            "-o",
            result_file,
        ]
        
        if is_compressed_file:
            command.extend(["--quiet", "image", "--input", image_name])
        else:
            command.extend(["--quiet", "image", image_name])
            
        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(f"The image {image_name} was scanned")

            return result_file

        except Exception as e:
            logger.error(f"Error during image scan of {image_name}: {e}")

    def _generate_sbom(self, prefix, image_name, remoteconfig, is_compressed_file=False):
        result_sbom = f"{image_name.replace('/', '_')}_SBOM.json"
        command = [
            prefix,
            "image",
            "--format",
            remoteconfig["TRIVY"]["SBOM_FORMAT"],
            "--output",
            result_sbom
        ]
        if is_compressed_file:
            command.extend(["--quiet", "--input", image_name])
        else:
            command.extend(["--quiet", image_name])
        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(f"SBOM generated and saved to: {result_sbom}")

            return get_list_component(result_sbom, remoteconfig["TRIVY"]["SBOM_FORMAT"])

        except Exception as e:
            logger.error(f"Error generating SBOM: {e}")

    def run_tool_container_sca(self, remoteconfig, secret_tool, token_engine_container, image_name, result_file, base_image, exclusions, generate_sbom, is_compressed_file=False):
        trivy_version = remoteconfig["TRIVY"]["TRIVY_VERSION"]
        os_platform = platform.system()
        arch_platform = platform.architecture()[0]
        base_url = f"https://github.com/aquasecurity/trivy/releases/download/v{trivy_version}/"
        sbom_components = None

        command_prefix = "trivy"
        if os_platform == "Linux":
            file=f"trivy_{trivy_version}_Linux-{arch_platform}.tar.gz"
            command_prefix = self.install_tool(file, base_url+file, "trivy")
        elif os_platform == "Darwin":
            file=f"trivy_{trivy_version}_macOS-{arch_platform}.tar.gz"
            command_prefix = self.install_tool(file, base_url+file, "trivy")
        elif os_platform == "Windows":
            file=f"trivy_{trivy_version}_windows-{arch_platform}.zip"
            command_prefix = self.install_tool_windows(file, base_url+file, "trivy.exe")
        else:
            logger.warning(f"{os_platform} is not supported.")
            return None

        image_scanned = (
            self.scan_image(command_prefix, image_name, result_file, base_image, is_compressed_file)
        )
        if generate_sbom:
            sbom_components = self._generate_sbom(command_prefix, image_name, remoteconfig, is_compressed_file)

        return image_scanned, sbom_components
