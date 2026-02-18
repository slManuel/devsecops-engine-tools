from devsecops_engine_tools.engine_utilities.dependency_track.domain.models.server_config import ServerConfig


def test_server_config_default_values():
    server_config = ServerConfig()
    assert server_config.host == ""
    assert server_config.api_key == ""


def test_server_config_with_values():
    server_config = ServerConfig(
        host="https://dependency-track.example.com",
        api_key="api-key-abc123",
    )
    assert server_config.host == "https://dependency-track.example.com"
    assert server_config.api_key == "api-key-abc123"


def test_server_config_is_dataclass():
    server_config = ServerConfig(host="http://localhost:8080", api_key="secret")
    assert server_config.host == "http://localhost:8080"
    assert server_config.api_key == "secret"
