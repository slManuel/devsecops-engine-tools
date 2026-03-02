from unittest.mock import patch, Mock
from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dependency_track import DependencyTrack
from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.server_config import ServerConfig
from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.sbom_upload import SbomUpload

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
def test_upload_sbom_400_invalid_bom_with_json_body(mock_read_sbom, mock_put):
    mock_read_sbom.return_value = SBOM_BASE64
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "type": "https://api.example.org/foo/bar/example-problem",
        "status": 400,
        "title": "Example title",
        "detail": "Example detail",
        "instance": "https://api.example.org/foo/bar/example-instance",
        "errors": ["string"],
    }
    mock_put.return_value = mock_response

    dt = DependencyTrack()
    token = dt.upload_sbom(make_config(), make_request())

    assert token is None



@patch(f"{MODULE_PATH}.requests.put")
@patch(f"{MODULE_PATH}.read_sbom_file_as_base64")
def test_upload_sbom_401_unauthorized(mock_read_sbom, mock_put):
    mock_read_sbom.return_value = SBOM_BASE64
    mock_response = Mock()
    mock_response.status_code = 401
    mock_put.return_value = mock_response

    dt = DependencyTrack()
    token = dt.upload_sbom(make_config(), make_request())

    assert token is None


@patch(f"{MODULE_PATH}.requests.put")
@patch(f"{MODULE_PATH}.read_sbom_file_as_base64")
def test_upload_sbom_403_forbidden(mock_read_sbom, mock_put):
    mock_read_sbom.return_value = SBOM_BASE64
    mock_response = Mock()
    mock_response.status_code = 403
    mock_put.return_value = mock_response

    dt = DependencyTrack()
    token = dt.upload_sbom(make_config(), make_request())

    assert token is None


@patch(f"{MODULE_PATH}.requests.put")
@patch(f"{MODULE_PATH}.read_sbom_file_as_base64")
def test_upload_sbom_404_project_not_found(mock_read_sbom, mock_put):
    mock_read_sbom.return_value = SBOM_BASE64
    mock_response = Mock()
    mock_response.status_code = 404
    mock_put.return_value = mock_response

    dt = DependencyTrack()
    token = dt.upload_sbom(make_config(), make_request())

    assert token is None


@patch(f"{MODULE_PATH}.requests.put")
@patch(f"{MODULE_PATH}.read_sbom_file_as_base64")
def test_upload_sbom_unexpected_status_code(mock_read_sbom, mock_put):
    mock_read_sbom.return_value = SBOM_BASE64
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_put.return_value = mock_response

    dt = DependencyTrack()
    token = dt.upload_sbom(make_config(), make_request())

    assert token is None


@patch(f"{MODULE_PATH}.read_sbom_file_as_base64")
def test_upload_sbom_file_not_found(mock_read_sbom):
    mock_read_sbom.side_effect = FileNotFoundError("bom.json not found")

    dt = DependencyTrack()
    token = dt.upload_sbom(make_config(), make_request())

    assert token is None
