import dataclasses


@dataclasses.dataclass
class SbomUploadResponse:
    token: str = ""

    @classmethod
    def from_dict(cls, obj):
        return cls(token=obj.get("token", ""))
