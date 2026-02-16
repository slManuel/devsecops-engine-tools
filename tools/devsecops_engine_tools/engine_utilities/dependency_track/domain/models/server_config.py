import dataclasses


@dataclasses.dataclass
class ServerConfig:
    host: str = ""
    api_key: str = ""