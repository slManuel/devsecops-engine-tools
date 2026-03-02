import dataclasses


@dataclasses.dataclass
class SbomUpload:
    project_name: str = ""
    project_version: str = ""
    sbom_filename: str = ""
