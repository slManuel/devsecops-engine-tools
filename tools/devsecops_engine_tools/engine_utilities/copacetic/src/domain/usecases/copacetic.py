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
        """
        Process container image patching using Copacetic
        """
        try:
            # Get configuration
            copacetic_config = self.remote_config_source_gateway.get_remote_config(
                args["remote_config_repo"], "/copacetic/ConfigTool.json", args["remote_config_branch"]
            )
            
            # Get secrets if needed
            if args["use_secrets_manager"] == "true":
                token_registry = self.secrets_manager_gateway.get_secret(
                    copacetic_config["SECRETS"]["TOKEN_REGISTRY"]
                )
            else:
                token_registry = args.get("token_registry")

            # Validate required parameters
            container_image = args.get("container_image")
            vulnerability_report = args.get("vulnerability_report")
            
            if not container_image:
                raise ValueError("Container image is required for Copacetic patching")
            
            if not vulnerability_report:
                raise ValueError("Vulnerability report is required for Copacetic patching")

            logger.info(f"Starting Copacetic patching for image: {container_image}")
            
            # Execute Copacetic patching
            patch_result = self.copacetic_gateway.patch_image(
                container_image=container_image,
                vulnerability_report=vulnerability_report,
                output_image=args.get("output_image"),
                patch_format=args.get("patch_format", "trivy"),
                registry_token=token_registry,
                registry_url=args.get("registry_url"),
                buildkit_addr=args.get("buildkit_addr"),
                config=copacetic_config
            )

            if patch_result["success"]:
                logger.info("Copacetic patching completed successfully")
                print(
                    self.devops_platform_gateway.message(
                        "succeeded",
                        f"Container image patched successfully: {patch_result['patched_image']}"
                    )
                )
                
                # Create summary report
                summary = {
                    "module": "copacetic",
                    "original_image": container_image,
                    "patched_image": patch_result["patched_image"],
                    "vulnerabilities_patched": patch_result.get("vulnerabilities_patched", 0),
                    "patch_details": patch_result.get("patch_details", [])
                }
                
                return summary
            else:
                error_msg = patch_result.get("error", "Unknown error during patching")
                logger.error(f"Copacetic patching failed: {error_msg}")
                print(
                    self.devops_platform_gateway.message(
                        "error",
                        f"Copacetic patching failed: {error_msg}"
                    )
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
