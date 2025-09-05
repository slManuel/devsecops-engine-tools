from abc import ABCMeta, abstractmethod
from typing import List, Optional, Any, Tuple
from devsecops_engine_tools.engine_sast.engine_code.src.domain.model.config_tool import ConfigTool

class ToolGateway(metaclass=ABCMeta):
    @abstractmethod
    def run_tool(
        self,
        folder_to_scan: str,
        pull_request_files: List[str],
        agent_work_folder: str,
        repository: str,
        config_tool: ConfigTool
    ) -> Tuple[List[Any], Optional[str]]:
        """
        Run the code scan tool.
        Args:
            folder_to_scan: Path to the folder to scan
            pull_request_files: List of files modified in the pull request
            agent_work_folder: Directory for storing temporary files
            repository: Name of the repository
            config_tool: Configuration object for the tool
        Returns:
            Tuple containing:
            - List of findings (vulnerabilities or defects).
            - Path to the results file, or None if no file is generated.
        """
        pass