from dataclasses import dataclass
from typing import Optional
import requests
from devsecops_engine_tools.engine_core.src.domain.model.gateway.license_manager import LicenseManagerGateway
from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.sbom_upload import SbomUpload

from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.server_config import ServerConfig
from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dto.sbom_request import SbomRequest
from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dto.sbom_response import SbomUploadResponse
from devsecops_engine_tools.engine_utilities.defect_dojo.infraestructure.driver_adapters.settings.settings import VERIFY_CERTIFICATE
from devsecops_engine_tools.engine_utilities.sbom.sbom_file_reader import read_sbom_file_as_base64
from devsecops_engine_tools.engine_utilities.settings import SETTING_LOGGER
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger

logger = MyLogger.__call__(**SETTING_LOGGER).get_logger()

_STATUS_ERROR_MESSAGES = {
    401: "Unauthorized (401): invalid or missing API key for license analyzer.",
    403: "Forbidden (403): access to the specified project is forbidden.",
    404: "Not Found (404): the project could not be found.",
}

@dataclass
class DependencyTrack(LicenseManagerGateway):

    def upload_sbom(self, config: ServerConfig, request: SbomUpload) -> Optional[str]:
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
                url=url, headers=headers, json=payload.to_dict(), verify=VERIFY_CERTIFICATE
            )
            if response.status_code == 200:
                return SbomUploadResponse.from_dict(response.json()).token

            if response.status_code == 400:
                error_body = response.json()
                logger.error(
                    f"Invalid BOM (400): {error_body.get('title', 'No title')} - "
                    f"{error_body.get('detail', 'No detail')} | "
                    f"errors: {error_body.get('errors', [])}"
                )
                return None

            if error_message := _STATUS_ERROR_MESSAGES.get(response.status_code):
                logger.error(error_message)
                return None

            logger.error(f"Unexpected error uploading SBOM: HTTP {response.status_code} - {response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Error uploading SBOM to license analyzer: {str(e)}")
            return None