import subprocess
import os
import json
import re
from typing import Dict, Optional
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


class CopaceticAdapter:
    """
    Adapter for Copacetic container image vulnerability patching tool
    """

    def __init__(self):
        self.copa_binary = self._find_copa_binary()

    def _find_copa_binary(self) -> str:
        try:
            result = subprocess.run(["which", "copa"], capture_output=True, text=True)
            if result.returncode == 0:
                return "copa"
        except FileNotFoundError:
            pass

        common_paths = [
            "/usr/local/bin/copa",
            "/usr/bin/copa",
            "/opt/copa/copa",
            "./copa"
        ]
        
        for path in common_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path

        return "copa"

    def patch_image(
        self,
        image: str,
        vulnerability_report: str,
        output_image: Optional[str] = None,
        patch_format: str = "trivy",
        config: Optional[Dict] = None
    ):
        try:
            config = config or {}
            buildkit_config = config.get("BUILDKIT_CONFIG", {})
            
            copa_cmd = [
                self.copa_binary, 
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
                copa_cmd.extend(["-t", output_image])
            else:
                tag_suffix = config.get("DEFAULT_OUTPUT_SUFFIX", "-patched")
                # Remove leading dash if present for --tag-suffix
                if tag_suffix.startswith("-"):
                    tag_suffix = tag_suffix[1:]
                copa_cmd.extend(["--tag-suffix", tag_suffix])
            
            # Add timeout configuration
            timeout_duration = config.get("TIMEOUT", 1800)
            copa_cmd.extend(["--timeout", f"{timeout_duration}s"])
            
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
            error_msg = f"Copa command timed out after {timeout_duration} seconds"
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
                        # Try to extract numbers that might indicate package count
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
            logger.error(f"Failed to parse Copa output: {str(e)}")
            return {"vulnerabilities_patched": 0, "details": [], "packages_updated": 0, "platforms_processed": []}

    def get_image_info(self, image: str) -> Dict:
        """
        Get basic information about a container image
        """
        try:
            # Try to inspect the image using docker
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
            logger.warning(f"Could not get image info for {image}: {str(e)}")
            return {"exists": False, "error": str(e)}

