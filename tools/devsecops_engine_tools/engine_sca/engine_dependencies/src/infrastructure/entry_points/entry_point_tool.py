from devsecops_engine_tools.engine_core.src.domain.model.gateway.license_manager import LicenseManagerGateway
from devsecops_engine_tools.engine_sca.engine_dependencies.src.domain.usecases.dependencies_sca_scan import (
    DependenciesScan,
)
from devsecops_engine_tools.engine_sca.engine_dependencies.src.domain.usecases.set_input_core import (
    SetInputCore,
)
from devsecops_engine_tools.engine_sca.engine_dependencies.src.domain.usecases.handle_remote_config_patterns import (
    HandleRemoteConfigPatterns,
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway import (
    DevopsPlatformGateway,
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.sbom_manager import (
    SbomManagerGateway,
)

import os

from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.sbom_upload import SbomUpload
from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.server_config import ServerConfig
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


def init_engine_dependencies(
    tool_run,
    tool_remote: DevopsPlatformGateway,
    remote_config_source_gateway: DevopsPlatformGateway,
    tool_deserializator,
    dict_args,
    secret_tool,
    config_tool,
    tool_sbom: SbomManagerGateway,
    tool_license_manager: LicenseManagerGateway,
):
    remote_config = remote_config_source_gateway.get_remote_config(
        dict_args["remote_config_repo"],
        "engine_sca/engine_dependencies/ConfigTool.json",
        dict_args["remote_config_branch"]
    )
    exclusions = remote_config_source_gateway.get_remote_config(
        dict_args["remote_config_repo"],
        "engine_sca/engine_dependencies/Exclusions.json",
        dict_args["remote_config_branch"]
    )
    pipeline_name = tool_remote.get_variable("pipeline_name")
    build_id = tool_remote.get_variable("build_id")
    build_url = tool_remote.get_build_pipeline_execution_url()

    handle_remote_config_patterns = HandleRemoteConfigPatterns(
        remote_config, exclusions, pipeline_name
    )
    skip_flag = handle_remote_config_patterns.skip_from_exclusion()
    scan_flag = handle_remote_config_patterns.ignore_analysis_pattern()

    dependencies_scanned = None
    deserialized = []
    sbom_components = None
    config_sbom = config_tool["SBOM_MANAGER"]
    config_license = config_tool["LICENSE_ANALYZER"]
    license_tool = config_license.get("TOOL")
    input_core = SetInputCore(
        remote_config,
        exclusions,
        pipeline_name,
        config_tool["ENGINE_DEPENDENCIES"]["TOOL"],
    )

    if scan_flag and not (skip_flag):
        to_scan = dict_args["folder_path"] if dict_args["folder_path"] else os.getcwd()        
        if os.path.exists(to_scan):
            dependencies_sca_scan = DependenciesScan(
                tool_run,
                tool_deserializator,
                remote_config,
                dict_args,
                exclusions,
                pipeline_name,
                to_scan,
                secret_tool,
                build_id,
                build_url
            )
            branch_filter = [branch for branch in config_sbom["BRANCH_FILTER"] if branch is not None]
            if config_sbom["ENABLED"] and (
                not branch_filter or 
                any(
                    branch in str(tool_remote.get_variable("branch_tag"))
                    for branch in branch_filter
                )
            ):
                sbom_components = tool_sbom.get_components(
                    to_scan,
                    config_sbom,
                    pipeline_name
                )

                if config_tool["LICENSE_ANALYZER"]["ENABLED"]:
                    token_license_analyzer = secret_tool.get_secret(config_license[license_tool]["API_KEY_SECRET_KEY"]) if secret_tool else dict_args.get("token_license_analyzer")
                    
                    if not token_license_analyzer:
                        logger.error("API key for license analyzer is not provided.")
                    else:
                        task_id=tool_license_manager.upload_sbom(
                            config=ServerConfig(
                                host=config_license[license_tool]["HOST"],
                                api_key=token_license_analyzer
                            ),
                            request=SbomUpload(
                                project_name=pipeline_name,
                                project_version=str(tool_remote.get_variable("branch_tag")),
                                sbom_filename=f"{pipeline_name}_SBOM.json"
                            )
                        )

                        logger.info(f"SBOM uploaded to license analyzer with task ID: {task_id}")
    
                        if config_license[license_tool].get("EXPORT_TASK_ID", False):
                            tool_remote.set_variable(config_license[license_tool]["TASK_ID_VARIABLE_NAME"],task_id)

            dependencies_scanned = dependencies_sca_scan.process()
            deserialized = (
                dependencies_sca_scan.deserializator(dependencies_scanned)
                if dependencies_scanned is not None
                else []
            )
        else:
            logger.error(f"Path {to_scan} does not exist")
    else:
        print("Tool skipped by DevSecOps policy")
        dict_args["send_metrics"] = "false"
        dict_args["use_vulnerability_management"] = "false"

    core_input = input_core.set_input_core(dependencies_scanned)

    return deserialized, core_input, sbom_components
