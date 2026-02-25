from dataclasses import dataclass
import requests
from devsecops_engine_tools.engine_core.src.domain.model.gateway.license_manager import LicenseManagerGateway
from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.sbom_upload import SbomUpload

from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.server_config import ServerConfig
from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dto.sbom_request import SbomRequest
from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dto.sbom_response import SbomUploadResponse
from devsecops_engine_tools.engine_utilities.utils.api_error import ApiError
from devsecops_engine_tools.engine_utilities.sbom.sbom_file_reader import read_sbom_file_as_base64
from devsecops_engine_tools.engine_utilities.settings import SETTING_LOGGER
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger

logger = MyLogger.__call__(**SETTING_LOGGER).get_logger()

@dataclass
class DependencyTrack(LicenseManagerGateway):

    def upload_sbom(self, config: ServerConfig, request: SbomUpload) -> str:        
        url = f"{config.host}/api/v1/bom"
        headers = {
            "X-Api-Key": config.api_key,
            "Content-Type": "application/json",
        }
        try:
            sbom_base64 = read_sbom_file_as_base64(request.sbom_filename)
            payload = SbomRequest(
                project_name=request.project_name,
                project_version=request.project_version,
                auto_create=True,
                bom=sbom_base64,
            )
            response = requests.put(
                url=url, headers=headers, json=payload.to_dict()
            )
            if response.status_code != 200:
                try:
                    error_body = response.json()
                except ValueError:
                    error_body = {"status_code": response.status_code, "body": response.text}
                logger.error(error_body)
                raise ApiError(error_body)
            try:
                response_data = response.json()
            except ValueError:
                raise ApiError({"message": f"Invalid JSON response from server: {response.text[:200]}"})
            token_response = SbomUploadResponse.from_dict(response_data)
            return token_response.token
        except Exception as e:
            raise ApiError(e)