import subprocess
import os
import json
import re
import platform
import requests
import tarfile
import tempfile
from typing import Dict, Optional
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


class CopaceticAdapter:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    def install_tool(self, version, path="."):
        try:
            installed = subprocess.run(
                ["which", "copa"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if installed.returncode == 0:
                return
        except FileNotFoundError:
            pass

        try:
            os_platform = platform.system()
            architecture = platform.machine()

            if os_platform == "Linux":
                if architecture == "aarch64" or architecture == "arm64":
                    arch = "arm64"
                else:
                    arch = "amd64"
                curr_os = "linux"
            elif os_platform == "Darwin":
                curr_os = "darwin"
            else:
                raise OSError(f"Copa installation is not supported on {os_platform}")

            url = f"https://github.com/project-copacetic/copacetic/releases/download/v{version}/copa_{version}_{curr_os}_{arch}.tar.gz"

            response = requests.get(url, allow_redirects=True)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            with tarfile.open(temp_path, 'r:gz') as tar:
                copa_member = None
                for member in tar.getmembers():
                    if member.name.endswith('copa') and member.isfile():
                        copa_member = member
                        break
                
                if copa_member:
                    tar.extract(copa_member, path=path)
                    extracted_path = os.path.join(path, copa_member.name)
                    if os.path.exists(extracted_path):
                        os.chmod(extracted_path, 0o755)

            os.unlink(temp_path)
            return extracted_path
            
        except requests.RequestException as error:
            logger.error(f"Error downloading Copa for {os_platform}: {error}")
        except tarfile.TarError as error:
            logger.error(f"Error extracting Copa archive: {error}")
        except Exception as error:
            logger.error(f"Error during Copa installation on {os_platform}: {error}")

    def patch_image(
        self,
        image: str,
        vulnerability_report: str,
        output_image: Optional[str] = None,
        patch_format: str = "trivy",
        config: Optional[Dict] = None,
        work_folder: str = "."
    ):
        try:
            config = config or {}
            buildkit_config = config.get("BUILDKIT_CONFIG", {})
            prefix = self.install_tool(config.get("VERSION"), path=work_folder)
            
            copa_cmd = [
                prefix,
                "patch",
                "--image",
                image,
                "--scanner",
                patch_format
            ]

            if vulnerability_report:
                copa_cmd.extend(["--report", vulnerability_report])
            
            buildkit_addr = buildkit_config.get("DEFAULT_ADDR")
            if buildkit_addr:
                copa_cmd.extend(["--addr", buildkit_addr])

            progress_mode = buildkit_config.get("PROGRESS", "auto")
            if progress_mode not in ["auto", "plain", "tty", "quiet", "rawjson"]:
                raise ValueError(f"Invalid progress mode: {progress_mode}")
            else:
                copa_cmd.extend(["--progress", progress_mode])
            
            if output_image:
                copa_cmd.extend(["--tag", output_image])
            else:
                tag_suffix = config.get("DEFAULT_OUTPUT_SUFFIX", "-patched")
                if tag_suffix.startswith("-"):
                    tag_suffix = tag_suffix[1:]
                copa_cmd.extend(["--tag-suffix", tag_suffix])

            timeout_duration = config.get("TIMEOUT", 5)
            copa_cmd.extend(["--timeout", f"{timeout_duration}m"])
            
            if buildkit_config.get("IGNORE_ERRORS", False):
                copa_cmd.append("--ignore-errors")
            
            result = subprocess.run(
                copa_cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("Copacetic patching completed successfully")

                patch_details = self._parse_copa_output(result.stdout)

                if output_image:
                    patched_image = output_image
                else:
                    tag_suffix = config.get("DEFAULT_OUTPUT_SUFFIX", "-patched")
                    if ":" in image:
                        base_image, tag = image.rsplit(":", 1)
                        patched_image = f"{base_image}:{tag}{tag_suffix}"
                    else:
                        patched_image = f"{image}{tag_suffix}"
                
                return {
                    "success": True,
                    "patched_image": patched_image,
                    "vulnerabilities_patched": patch_details.get("vulnerabilities_patched", 0),
                    "patch_details": patch_details.get("details", []),
                    "copa_output": result.stdout
                }
            else:
                error_msg = f"Copa command failed with return code {result.returncode}. Error: {result.stderr}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "copa_output": result.stdout,
                    "copa_error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            error_msg = f"Copa command timed out after {timeout_duration} minutes"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error during Copa execution: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def _parse_copa_output(self, output: str) -> Dict:
        try:
            details = {
                "vulnerabilities_patched": 0,
                "details": [],
                "packages_updated": 0,
                "platforms_processed": []
            }
            
            lines = output.split('\n')
            current_platform = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse platform information
                if "platform" in line.lower() and ("linux/" in line.lower() or "amd64" in line.lower() or "arm64" in line.lower()):
                    if current_platform not in details["platforms_processed"]:
                        details["platforms_processed"].append(current_platform or "linux/amd64")
                
                # Parse patched vulnerabilities
                if any(keyword in line.lower() for keyword in ["patched", "fixed", "updated", "resolved"]):
                    details["details"].append(line)
                
                # Parse package updates
                if any(keyword in line.lower() for keyword in ["package", "upgrade", "install"]):
                    if any(char.isdigit() for char in line):
                        import re
                        numbers = re.findall(r'\d+', line)
                        if numbers:
                            details["packages_updated"] += int(numbers[0])
                
                # Try to extract vulnerability counts
                if any(keyword in line.lower() for keyword in ["vulnerabilities", "cves", "security"]):
                    if any(char.isdigit() for char in line):
                        import re
                        numbers = re.findall(r'\d+', line)
                        for num in numbers:
                            if int(num) > details["vulnerabilities_patched"]:
                                details["vulnerabilities_patched"] = int(num)
                
                # Parse success indicators
                if any(keyword in line.lower() for keyword in ["completed", "success", "finished", "done"]):
                    details["details"].append(f"Status: {line}")
            
            # Default platform if none detected
            if not details["platforms_processed"]:
                details["platforms_processed"].append("linux/amd64")
            
            return details
            
        except Exception as e:
            print(f"Failed to parse Copa output: {str(e)}")
            return {"vulnerabilities_patched": 0, "details": [], "packages_updated": 0, "platforms_processed": []}

    def get_image_info(self, image: str) -> Dict:
        try:
            result = subprocess.run(
                ["docker", "inspect", image],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                import json
                image_data = json.loads(result.stdout)
                
                if image_data:
                    info = image_data[0]
                    return {
                        "exists": True,
                        "created": info.get("Created"),
                        "architecture": info.get("Architecture"),
                        "os": info.get("Os"),
                        "size": info.get("Size"),
                        "layers": len(info.get("RootFS", {}).get("Layers", [])),
                        "config": info.get("Config", {})
                    }
            
            return {"exists": False}
            
        except Exception as e:
            print(f"Could not get image info for {image}: {str(e)}")
            return {"exists": False, "error": str(e)}
