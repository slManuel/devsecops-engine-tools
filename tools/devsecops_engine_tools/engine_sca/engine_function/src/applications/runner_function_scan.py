from devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.entry_points.entry_point_tool import (
    init_engine_sca_rm,
)
from devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan import (
    PrismaCloudManagerScan,
)
from devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_deserialize_output import (
    PrismaDeserealizator,
)


def runner_engine_function(dict_args, config_tool, token,tool_remote):
    try:
        engine_type = dict_args["tool"].upper()
        if config_tool[engine_type]["TOOL"].lower() == "prisma":
            tool_run = PrismaCloudManagerScan(config_tool, dict_args)
            tool_deseralizator = PrismaDeserealizator()
        return init_engine_sca_rm(
            tool_run,
            tool_remote,
            tool_deseralizator,
            dict_args,
            token,
            config_tool,
        )

    except Exception as e:
        raise Exception(f"Error SCAN engine function : {str(e)}")


if __name__ == "__main__":
    runner_engine_function()
