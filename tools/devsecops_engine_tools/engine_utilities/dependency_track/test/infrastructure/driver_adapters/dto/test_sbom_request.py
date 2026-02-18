from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.dto.sbom_request import SbomRequest


def test_sbom_request_default_values():
    request = SbomRequest()
    assert request.project is None
    assert request.project_name is None
    assert request.project_version is None
    assert request.project_tags is None
    assert request.auto_create is None
    assert request.parent_uuid is None
    assert request.parent_name is None
    assert request.parent_version is None
    assert request.is_latest_project_version is None
    assert request.bom == ""


def test_sbom_request_to_dict_excludes_none():
    request = SbomRequest(
        project_name="my-project",
        project_version="1.0.0",
        auto_create=True,
        bom="base64encodedcontent==",
    )
    result = request.to_dict()
    assert "projectName" in result
    assert result["projectName"] == "my-project"
    assert result["projectVersion"] == "1.0.0"
    assert result["autoCreate"] is True
    assert result["bom"] == "base64encodedcontent=="
    assert "project" not in result
    assert "projectTags" not in result
    assert "parentUUID" not in result
    assert "parentName" not in result
    assert "parentVersion" not in result
    assert "isLatestProjectVersion" not in result


def test_sbom_request_to_dict_with_parent_uuid_alias():
    request = SbomRequest(
        project_name="service",
        parent_uuid="uuid-1234-5678",
        bom="dGVzdA==",
    )
    result = request.to_dict()
    assert result["parentUUID"] == "uuid-1234-5678"
    assert result["projectName"] == "service"


def test_sbom_request_to_dict_with_all_fields():
    request = SbomRequest(
        project="proj-uuid",
        project_name="my-service",
        project_version="2.0.0",
        project_tags=["tag1", "tag2"],
        auto_create=False,
        parent_uuid="parent-uuid",
        parent_name="parent-project",
        parent_version="1.0.0",
        is_latest_project_version=True,
        bom="Y29udGVudA==",
    )
    result = request.to_dict()
    assert result["project"] == "proj-uuid"
    assert result["projectName"] == "my-service"
    assert result["projectVersion"] == "2.0.0"
    assert result["projectTags"] == ["tag1", "tag2"]
    assert result["autoCreate"] is False
    assert result["parentUUID"] == "parent-uuid"
    assert result["parentName"] == "parent-project"
    assert result["parentVersion"] == "1.0.0"
    assert result["isLatestProjectVersion"] is True
    assert result["bom"] == "Y29udGVudA=="
