from abc import ABCMeta, abstractmethod


class ToolGateway(metaclass=ABCMeta):
    @abstractmethod
    def run_tool_container_sca(self, dict_args, secret_tool, token_engine_container, scan_image, release, base_image, exclusions, generate_sbom, docker_address, is_compressed_file=False):
        "run tool container sca"

    @abstractmethod
    def get_container_context_from_results(self, path_file_results: str) -> None:
        "get_container_context_from_results"
