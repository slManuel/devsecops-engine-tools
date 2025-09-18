from devsecops_engine_tools.engine_sca.engine_function.src.domain.usecases.function_sca_scan import (
    FunctionScaScan,
)
from devsecops_engine_tools.engine_sca.engine_function.src.domain.usecases.handle_remote_config_patterns import (
    HandleRemoteConfigPatterns,
)
from devsecops_engine_tools.engine_sca.engine_function.src.domain.usecases.set_input_core import (
    SetInputCore,
)


def init_engine_sca_rm(
    tool_run,
    tool_remote,
    tool_deseralizator,
    dict_args,
    token,
    config_tool,
):
    handle_remote_config_patterns = HandleRemoteConfigPatterns(tool_remote, dict_args)
    function_sca_scan = FunctionScaScan(
        tool_run,
        tool_remote,
        tool_deseralizator,
        dict_args,
        token,
        handle_remote_config_patterns.process_handle_skip_tool(),
    )
    input_core = SetInputCore(tool_remote, dict_args, config_tool)
    function_scan = function_sca_scan.process()

    return function_sca_scan.deseralizator(function_scan), input_core.set_input_core()
