class Alias:
    """Annotation to override the serialized key name for a dataclass field.

    Usage:
        from typing import Annotated, Optional
        from devsecops_engine_tools.engine_utilities.utils.alias import Alias

        parent_uuid: Annotated[Optional[str], Alias("parentUUID")] = None
    """

    def __init__(self, name: str):
        self.name = name
