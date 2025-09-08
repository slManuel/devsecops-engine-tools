from devsecops_engine_tools.engine_sast.engine_code.src.infrastructure.entry_points.entry_point_tool import (
    init_engine_sast_code,
)
from devsecops_engine_tools.engine_sast.engine_code.src.infrastructure.driven_adapters.bearer.bearer_tool import (
    BearerTool
)
from devsecops_engine_tools.engine_utilities.git_cli.infrastructure.git_run import (
    GitRun
)
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings
from devsecops_engine_tools.engine_sast.engine_code.src.infrastructure.driven_adapters.kiuwan.kiuwan_tool import get_kiuwan_instance


logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

def runner_engine_code(dict_args, tool, devops_platform_gateway, remote_config_source_gateway):
    try:
        logger.info("Selecting tool...")
        tool_gateway = None
        git_gateway = GitRun()
        if (tool == "BEARER"):
            logger.info("Bearer tool selected...")
            tool_gateway = BearerTool()
        elif (tool == "KIUWAN"):
            logger.info("Kiuwan tool selected...")
            tool_gateway = get_kiuwan_instance(
                dict_args=dict_args,
                devops_platform_gateway=devops_platform_gateway,
            )
        
        logger.info("Tool has been selected successfully")

        return init_engine_sast_code(
            devops_platform_gateway=devops_platform_gateway,
            remote_config_source_gateway=remote_config_source_gateway,
            tool_gateway=tool_gateway,
            dict_args=dict_args,
            git_gateway=git_gateway,
            tool=tool,
        )

    except Exception as e:
        raise Exception(f"Error engine_code : {str(e)}")


if __name__ == "__main__":
    runner_engine_code()