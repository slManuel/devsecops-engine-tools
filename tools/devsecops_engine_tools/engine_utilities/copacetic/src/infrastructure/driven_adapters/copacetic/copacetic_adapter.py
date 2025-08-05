import subprocess
import json
import os
import tempfile
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
        """
        Find the Copa binary in the system
        """
        # Check if copa is in PATH
        try:
            result = subprocess.run(["which", "copa"], capture_output=True, text=True)
            if result.returncode == 0:
                return "copa"
        except FileNotFoundError:
            pass
        
        # Check common installation paths
        common_paths = [
            "/usr/local/bin/copa",
            "/usr/bin/copa",
            "/opt/copa/copa",
            "./copa"
        ]
        
        for path in common_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        # Default to 'copa' and let it fail if not found
        return "copa"

    def patch_image(
        self,
        container_image: str,
        vulnerability_report: str,
        output_image: Optional[str] = None,
        patch_format: str = "trivy",
        registry_token: Optional[str] = None,
        registry_url: Optional[str] = None,
        buildkit_addr: Optional[str] = None,
        config: Optional[Dict] = None
    ) -> Dict:
        """
        Patch a container image using Copacetic
        
        Args:
            container_image: The container image to patch
            vulnerability_report: Path to the vulnerability report file
            output_image: Output image name (optional)
            patch_format: Format of the vulnerability report (trivy, grype)
            registry_token: Token for registry authentication
            registry_url: Registry URL
            buildkit_addr: BuildKit daemon address
            config: Additional configuration from ConfigTool.json
            
        Returns:
            Dict with patching results
        """
        try:
            logger.info(f"Starting Copacetic patching for image: {container_image}")
            
            # Prepare Copa command
            copa_cmd = [self.copa_binary, "patch"]
            
            # Add image
            copa_cmd.extend(["-i", container_image])
            
            # Add vulnerability report
            copa_cmd.extend(["-r", vulnerability_report])
            
            # Add report format
            copa_cmd.extend(["-f", patch_format])
            
            # Add output image if specified
            if output_image:
                copa_cmd.extend(["-t", output_image])
            else:
                # Generate output image name
                output_image = f"{container_image}-patched"
                copa_cmd.extend(["-t", output_image])
            
            # Add BuildKit address if specified
            if buildkit_addr:
                copa_cmd.extend(["--addr", buildkit_addr])
            
            # Set environment variables for registry authentication
            env = os.environ.copy()
            
            if registry_token and registry_url:
                # Set docker config for authentication
                docker_config = self._create_docker_config(registry_url, registry_token)
                if docker_config:
                    env["DOCKER_CONFIG"] = docker_config
            
            # Add timeout configuration
            if config and "TIMEOUT" in config:
                copa_cmd.extend(["--timeout", str(config["TIMEOUT"])])
            
            logger.info(f"Executing Copa command: {' '.join([cmd for cmd in copa_cmd if not cmd.startswith('auth')])}")
            
            # Execute Copa command
            result = subprocess.run(
                copa_cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=config.get("TIMEOUT", 1800) if config else 1800  # 30 minutes default
            )
            
            if result.returncode == 0:
                logger.info("Copacetic patching completed successfully")
                
                # Parse output to get patch details
                patch_details = self._parse_copa_output(result.stdout)
                
                return {
                    "success": True,
                    "patched_image": output_image,
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
            error_msg = "Copa command timed out"
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

    def _create_docker_config(self, registry_url: str, token: str) -> Optional[str]:
        """
        Create a temporary Docker config for registry authentication
        """
        try:
            temp_dir = tempfile.mkdtemp()
            config_path = os.path.join(temp_dir, "config.json")
            
            # Create Docker config
            docker_config = {
                "auths": {
                    registry_url: {
                        "auth": token
                    }
                }
            }
            
            with open(config_path, 'w') as f:
                json.dump(docker_config, f)
            
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to create Docker config: {str(e)}")
            return None

    def _parse_copa_output(self, output: str) -> Dict:
        """
        Parse Copa output to extract patching details
        """
        try:
            details = {
                "vulnerabilities_patched": 0,
                "details": []
            }
            
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                
                # Parse different types of output
                if "patched" in line.lower():
                    details["details"].append(line)
                
                # Try to extract number of vulnerabilities patched
                if "vulnerabilities" in line.lower() and any(char.isdigit() for char in line):
                    words = line.split()
                    for word in words:
                        if word.isdigit():
                            details["vulnerabilities_patched"] = int(word)
                            break
            
            return details
            
        except Exception as e:
            logger.error(f"Failed to parse Copa output: {str(e)}")
            return {"vulnerabilities_patched": 0, "details": []}

    def check_copa_availability(self) -> bool:
        """
        Check if Copa is available and working
        """
        try:
            result = subprocess.run(
                [self.copa_binary, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_copa_version(self) -> Optional[str]:
        """
        Get Copa version
        """
        try:
            result = subprocess.run(
                [self.copa_binary, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
