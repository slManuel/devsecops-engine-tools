from abc import ABCMeta, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from devsecops_engine_tools.engine_sast.engine_iac.src.domain.model.context_iac import ContextIac


class ToolGateway(metaclass=ABCMeta):
    @abstractmethod
    def run_tool(self, config_tool, folders_to_scan, **kwargs):
        "run_tool"

    @abstractmethod
    def get_iac_context_from_results(self, path_file_results) -> List['ContextIac']:
        "get_iac_context_from_results"
