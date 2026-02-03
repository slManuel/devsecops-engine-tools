from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.sbom_upload import SbomUpload

from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dto.sbom_request import SbomRequest
from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dto.sbom_response import SbomUploadResponse
from devsecops_engine_tools.engine_utilities.utils.api_error import ApiError
from devsecops_engine_tools.engine_utilities.defect_dojo.infraestructure.driver_adapters.settings.settings import VERIFY_CERTIFICATE
from devsecops_engine_tools.engine_utilities.utils.session_manager import SessionManager
from devsecops_engine_tools.engine_utilities.settings import SETTING_LOGGER
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger

logger = MyLogger.__call__(**SETTING_LOGGER).get_logger()


class SbomRestConsumer:
    def __init__(self, session: SessionManager):
        self.__token = session._token
        self.__host = session._host
        self.__session = session._instance

    def upload_sbom(self, request: SbomUpload) -> str:
        url = f"{self.__host}/api/v1/bom"
        headers = {
            "X-Api-Key": {self.__token},
            "Content-Type": "application/json",
        }
        try:
            adapter_request = SbomRequest(
                project_name=request.project_name,
                project_version=request.project_version,
                auto_create=request.auto_create,
                sbom=request.sbom,
            )
            response = self.__session.put(
                url=url, headers=headers, json=adapter_request.to_dict()
            )
            if response.status_code != 200:
                logger.error(response.json())
                raise ApiError(response.json())
            token_response = SbomUploadResponse.from_dict(response.json())
            return token_response.token
        except Exception as e:
            raise ApiError(e)