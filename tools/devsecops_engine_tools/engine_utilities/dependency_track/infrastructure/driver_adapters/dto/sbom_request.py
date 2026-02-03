import dataclasses


@dataclasses.dataclass
class SbomRequest:
    project: str = ""
    project_name: str = ""
    project_version: str = ""
    project_tags: list = dataclasses.field(default_factory=list)
    auto_create: bool = True
    parent_uuid: str = ""
    parent_name: str = ""
    parent_version: str = ""
    is_latest_project_version: bool = False
    bom: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)