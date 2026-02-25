import dataclasses
from typing import Annotated, Optional

from devsecops_engine_tools.engine_utilities.utils.alias import Alias
from devsecops_engine_tools.engine_utilities.utils.dataclass_classmethod import FromDictMixin


@dataclasses.dataclass
class SbomRequest(FromDictMixin):
    _exclude_none = True

    project: Optional[str] = None
    project_name: Optional[str] = None
    project_version: Optional[str] = None
    project_tags: Optional[list] = None
    auto_create: Optional[bool] = None
    parent_uuid: Annotated[Optional[str], Alias("parentUUID")] = None
    parent_name: Optional[str] = None
    parent_version: Optional[str] = None
    is_latest_project_version: Optional[bool] = None
    bom: str = ""