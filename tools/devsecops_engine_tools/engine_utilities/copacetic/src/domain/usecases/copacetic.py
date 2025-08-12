from devsecops_engine_tools.engine_core.src.domain.model.gateway.vulnerability_management_gateway import (
    VulnerabilityManagementGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.secrets_manager_gateway import (
    SecretsManagerGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway import (
    DevopsPlatformGateway
)
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings
import json

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


class Copacetic:
    def __init__(
        self,
        vulnerability_management_gateway: VulnerabilityManagementGateway,
        secrets_manager_gateway: SecretsManagerGateway,
        devops_platform_gateway: DevopsPlatformGateway,
        remote_config_source_gateway: DevopsPlatformGateway,
        copacetic_gateway,
    ):
        self.vulnerability_management_gateway = vulnerability_management_gateway
        self.secrets_manager_gateway = secrets_manager_gateway
        self.devops_platform_gateway = devops_platform_gateway
        self.remote_config_source_gateway = remote_config_source_gateway
        self.copacetic_gateway = copacetic_gateway

    def process(self, args):
        try:
            copacetic_config = self.remote_config_source_gateway.get_remote_config(
                args["remote_config_repo"], "/copacetic/ConfigTool.json", args["remote_config_branch"]
            )

            image = args.get("image")
            vulnerability_report = args.get("vulnerability_report")
            patch_format = args.get("patch_format", "trivy")
            
            if not image:
                raise ValueError("Image is required for Copacetic patching")

            print(f"Starting Copacetic patching for image: {image}")

            image_info = {}
            if hasattr(self.copacetic_gateway, 'get_image_info'):
                image_info = self.copacetic_gateway.get_image_info(image)
                if not image_info.get("exists", False):
                    print(f"Image {image} may not exist locally. Copacetic will attempt to pull it.")

            patch_result = self.copacetic_gateway.patch_image(
                image=image,
                vulnerability_report=vulnerability_report,
                output_image=args.get("output_image"),
                patch_format=patch_format,
                config=copacetic_config
            )

            if patch_result["success"]:
                logger.info("Copacetic patching completed successfully")
                
                success_msg = f"Container image patched successfully: {patch_result['patched_image']}"
                if patch_result.get("vulnerabilities_patched", 0) > 0:
                    success_msg += f" ({patch_result['vulnerabilities_patched']} vulnerabilities addressed)"
                
                print(
                    self.devops_platform_gateway.message("succeeded", success_msg)
                )
                
                # Create enhanced summary report
                summary = {
                    "module": "copacetic",
                    "original_image": image,
                    "patched_image": patch_result["patched_image"],
                    "vulnerabilities_patched": patch_result.get("vulnerabilities_patched", 0),
                    "packages_updated": patch_result.get("packages_updated", 0),
                    "platforms_processed": patch_result.get("platforms_processed", []),
                    "patch_details": patch_result.get("patch_details", []),
                    "output_format": patch_result.get("output_format", "openvex"),
                    "patch_format": patch_format,
                    "configuration_used": {
                        "timeout": copacetic_config.get("TIMEOUT", 1800),
                        "buildkit_addr": copacetic_config.get("BUILDKIT_CONFIG", {}).get("DEFAULT_ADDR")
                    }
                }
                
                if image_info.get("exists", False):
                    summary["original_image_info"] = {
                        "architecture": image_info.get("architecture"),
                        "os": image_info.get("os"),
                        "layers": image_info.get("layers")
                    }
                
                return summary
            else:
                error_msg = patch_result.get("error", "Unknown error during patching")
                logger.error(f"Copacetic patching failed: {error_msg}")
                
                detailed_error = f"Copacetic patching failed: {error_msg}"
                if patch_result.get("copa_error"):
                    detailed_error += f"\nCopa stderr: {patch_result['copa_error']}"
                
                print(
                    self.devops_platform_gateway.message("error", detailed_error)
                )
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"Error in Copacetic process: {str(e)}")
            print(
                self.devops_platform_gateway.message(
                    "error",
                    f"Error in Copacetic process: {str(e)}"
                )
            )
            raise e
