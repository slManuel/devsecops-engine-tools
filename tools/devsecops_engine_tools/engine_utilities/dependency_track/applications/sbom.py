from devsecops_engine_tools.engine_utilities.dependency_track.domain.user_case.sbom import SbomUserCase
from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.sbom import SbomRestConsumer
from devsecops_engine_tools.engine_utilities.utils.api_error import ApiError
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities.defect_dojo.domain.user_case.component import ComponentUserCase
from devsecops_engine_tools.engine_utilities.settings import SETTING_LOGGER

logger = MyLogger.__call__(**SETTING_LOGGER).get_logger()

class Sbom:

    @staticmethod
    def get_component(session, request: dict):
        try:
            rest_component = SbomRestConsumer(session=session)
            uc = SbomUserCase(rest_component)
            return uc.upload(request)
        except ApiError as e:
            logger.error(f"Error during upload sbom: {e}")
            raise e
