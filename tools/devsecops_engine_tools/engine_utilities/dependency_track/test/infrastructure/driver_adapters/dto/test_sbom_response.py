from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dto.sbom_response import SbomUploadResponse


def test_sbom_upload_response_default_values():
    response = SbomUploadResponse()
    assert response.token == ""


def test_sbom_upload_response_from_dict_with_token():
    data = {"token": "abc123-upload-token"}
    response = SbomUploadResponse.from_dict(data)
    assert response.token == "abc123-upload-token"


def test_sbom_upload_response_from_dict_missing_token():
    data = {}
    response = SbomUploadResponse.from_dict(data)
    assert response.token == ""


def test_sbom_upload_response_with_value():
    response = SbomUploadResponse(token="my-token-xyz")
    assert response.token == "my-token-xyz"
