from abc import ABCMeta, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from devsecops_engine_tools.engine_sca.engine_dependencies.src.domain.model.context_dependencies import ContextDependencies


class ToolGateway(metaclass=ABCMeta):
    @abstractmethod
    def run_tool_dependencies_sca(
        self, remote_config, dict_args,to_scan, secret_tool, token_engine_dependencies, **kwargs
    ) -> str:
        "run tool dependencies sca"
    
    @abstractmethod
    def get_dependencies_context_from_results(self, path_file_results, **kwargs) -> List['ContextDependencies']:
        "get_dependencies_context_from_results"