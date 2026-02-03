import dataclasses


@dataclasses.dataclass
class SbomUpload:
    project_name: str = ""
    project_version: str = ""
    auto_create: bool = True
    sbom: str = ""
