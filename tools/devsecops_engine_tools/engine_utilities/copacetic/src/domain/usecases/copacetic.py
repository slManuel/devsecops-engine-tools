from devsecops_engine_tools.engine_core.src.domain.model.gateway.vulnerability_management_gateway import (
    VulnerabilityManagementGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.secrets_manager_gateway import (
    SecretsManagerGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway import (
    DevopsPlatformGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.input_core import InputCore
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings
import shutil

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
                args["remote_config_repo"], "/engine_integrations/copacetic/ConfigTool.json", args["remote_config_branch"]
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
                config=copacetic_config,
                work_folder=self.devops_platform_gateway.get_variable("path_directory"),
                platform=args.get("platform")
            )

            if patch_result["success"]:
                logger.info("Copacetic patching completed successfully")

                if image_info.get("exists", False):
                    patch_result["original_image_info"] = {
                        "architecture": image_info.get("architecture"),
                        "os": image_info.get("os"),
                        "size": image_info.get("size"),
                        "layers": image_info.get("layers")
                    }

                self._print_results_table(patch_result)
            else:
                detailed_error = f"Copacetic patching failed for {image}: {patch_result.get('error', 'Unknown error')}"
                if patch_result.get("copa_error"):
                    detailed_error += f"\nCopa stderr: {patch_result['copa_error']}"
                
                print(
                    self.devops_platform_gateway.message("error", detailed_error)
                )

            return InputCore(
                totalized_exclusions=[],
                threshold_defined=None,
                path_file_results=patch_result.get("output_file", ""),
                custom_message_break_build=f"Copacetic patching completed for {image}",
                scope_pipeline="",
                scope_service="",
                stage_pipeline=self.devops_platform_gateway.get_variable("stage")
            )

        except Exception as e:
            logger.error(f"Error in Copacetic process: {str(e)}")
            print(
                self.devops_platform_gateway.message(
                    "error",
                    f"Error in Copacetic process: {str(e)}"
                )
            )

    def _print_results_table(self, summary):
        try:
            terminal_width = min(shutil.get_terminal_size().columns, 100)
        except:
            terminal_width = 100
        
        print(f"\n{'='*terminal_width}")
        title = " COPACETIC PATCHING RESULTS "
        padding = (terminal_width - len(title)) // 2
        print(f"{' '*padding}{title}{' '*padding}")
        print(f"{'='*terminal_width}")
        
        print(f"\n IMAGE INFORMATION:")
        print(f"   Original Image: {summary['original_image']}")
        print(f"   Patched Image:  {summary['patched_image']}")
        
        print(f"\n PATCHING STATISTICS:")
        vuln_count = summary.get('vulnerabilities_patched', 0)
        pkg_count = summary.get('packages_updated', 0)
        
        print(f"   Vulnerabilities Patched: {vuln_count}")
        print(f"   Packages Updated:        {pkg_count}")
        
        platforms = summary.get('platforms_processed', [])
        if platforms:
            print(f"   Platforms Processed:     {', '.join(platforms)}")
        
        if summary.get('original_image_info'):
            info = summary['original_image_info']
            print(f"\n  IMAGE DETAILS:")
            print(f"   Architecture: {info.get('architecture', 'N/A')}")
            print(f"   OS:           {info.get('os', 'N/A')}")
            print(f"   Size:         {info.get('size', 'N/A')}")
            print(f"   Layers:       {info.get('layers', 'N/A')}")

        patch_details = summary.get('patch_details', [])
        if patch_details:
            print(f"\n PATCH DETAILS:")
            
            for i, detail in enumerate(patch_details, 1):
                if isinstance(detail, dict):
                    cve = detail.get('vulnerability', detail.get('id', f'PATCH-{i}'))
                    print(f"   {cve}")

                    packages = detail.get('packages', [])
                    if not packages:
                        single_package = detail.get('package', detail.get('component'))
                        if single_package:
                            packages = [single_package]

                    for pkg in packages:
                        if isinstance(pkg, dict):
                            pkg_name = pkg.get('name', pkg.get('package', 'Unknown'))
                            version = pkg.get('version', pkg.get('fixed_version', ''))
                            if version:
                                print(f"       {pkg_name} (v{version})")
                            else:
                                print(f"       {pkg_name}")
                        else:
                            print(f"       {pkg}")

                    if not packages:
                        print(f"       No package information available")
                    
                else:
                    print(f"   {detail}")

                if i < len(patch_details):
                    print()
        
        print(f"\n SUMMARY:")
        if vuln_count > 0:
            print(f"   Status: SUCCESS - {vuln_count} vulnerabilities were patched")
        else:
            print(f"   Status: COMPLETED - No vulnerabilities found to patch")
        
        print(f"{'='*terminal_width}\n")
