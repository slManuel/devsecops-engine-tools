import pytest
from unittest.mock import patch, Mock
from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dependency_track import DependencyTrack
from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.server_config import ServerConfig
from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.sbom_upload import SbomUpload
from devsecops_engine_tools.engine_utilities.utils.api_error import ApiError

SBOM_BASE64 = "c2JvbWNvbnRlbnQ="

MODULE_PATH = "devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dependency_track"


def make_config():
    return ServerConfig(host="https://dt.example.com", api_key="test-api-key")


def make_request():
    return SbomUpload(project_name="my-project", project_version="1.0.0", sbom_filename="bom.json")


@patch(f"{MODULE_PATH}.requests.put")
@patch(f"{MODULE_PATH}.read_sbom_file_as_base64")
def test_upload_sbom_success(mock_read_sbom, mock_put):
    mock_read_sbom.return_value = SBOM_BASE64
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"token": "upload-token-abc"}
    mock_put.return_value = mock_response

    dt = DependencyTrack()
    token = dt.upload_sbom(make_config(), make_request())

    assert token == "upload-token-abc"
    mock_read_sbom.assert_called_once_with("bom.json")
    mock_put.assert_called_once()


@patch(f"{MODULE_PATH}.requests.put")
@patch(f"{MODULE_PATH}.read_sbom_file_as_base64")
def test_upload_sbom_non_200_with_json_error_body(mock_read_sbom, mock_put):
    mock_read_sbom.return_value = SBOM_BASE64
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"message": "Bad Request"}
    mock_put.return_value = mock_response

    dt = DependencyTrack()
    with pytest.raises(ApiError):
        dt.upload_sbom(make_config(), make_request())


@patch(f"{MODULE_PATH}.requests.put")
@patch(f"{MODULE_PATH}.read_sbom_file_as_base64")
def test_upload_sbom_non_200_with_non_json_body(mock_read_sbom, mock_put):
    mock_read_sbom.return_value = SBOM_BASE64
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.side_effect = ValueError("No JSON object")
    mock_response.text = "Internal Server Error"
    mock_put.return_value = mock_response

    dt = DependencyTrack()
    with pytest.raises(ApiError):
        dt.upload_sbom(make_config(), make_request())


@patch(f"{MODULE_PATH}.requests.put")
@patch(f"{MODULE_PATH}.read_sbom_file_as_base64")
def test_upload_sbom_200_invalid_json_response(mock_read_sbom, mock_put):
    mock_read_sbom.return_value = SBOM_BASE64
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_response.text = "unexpected response body"
    mock_put.return_value = mock_response

    dt = DependencyTrack()
    with pytest.raises(ApiError):
        dt.upload_sbom(make_config(), make_request())


@patch(f"{MODULE_PATH}.read_sbom_file_as_base64")
def test_upload_sbom_file_not_found(mock_read_sbom):
    mock_read_sbom.side_effect = FileNotFoundError("bom.json not found")

    dt = DependencyTrack()
    with pytest.raises(ApiError):
        dt.upload_sbom(make_config(), make_request())
