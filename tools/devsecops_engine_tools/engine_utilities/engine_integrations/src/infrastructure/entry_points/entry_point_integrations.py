def init_engine_integrations(args):
    pass

from devsecops_engine_tools.engine_utilities.engine_integrations.src.domain.usecases.handle_integrations import (
    Integrations
)
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


def init_engine_integrations(
    vulnerability_management_gateway,
    secrets_manager_gateway,
    devops_platform_gateway,
    remote_config_source_gateway,
    metrics_manager_gateway,
    args,
):
    return Integrations(
        vulnerability_management_gateway=vulnerability_management_gateway,
        secrets_manager_gateway=secrets_manager_gateway,
        devops_platform_gateway=devops_platform_gateway,
        remote_config_source_gateway=remote_config_source_gateway,
        metrics_manager_gateway=metrics_manager_gateway,
    ).process(args)
