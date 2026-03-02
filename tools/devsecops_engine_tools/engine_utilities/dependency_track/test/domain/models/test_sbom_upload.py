from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.sbom_upload import SbomUpload


def test_sbom_upload_default_values():
    sbom_upload = SbomUpload()
    assert sbom_upload.project_name == ""
    assert sbom_upload.project_version == ""
    assert sbom_upload.sbom_filename == ""


def test_sbom_upload_with_values():
    sbom_upload = SbomUpload(
        project_name="my-project",
        project_version="1.0.0",
        sbom_filename="bom.json",
    )
    assert sbom_upload.project_name == "my-project"
    assert sbom_upload.project_version == "1.0.0"
    assert sbom_upload.sbom_filename == "bom.json"


def test_sbom_upload_is_dataclass():
    sbom_upload = SbomUpload(project_name="app", project_version="2.5.1", sbom_filename="sbom.json")
    assert sbom_upload.project_name == "app"
    assert sbom_upload.project_version == "2.5.1"
    assert sbom_upload.sbom_filename == "sbom.json"
