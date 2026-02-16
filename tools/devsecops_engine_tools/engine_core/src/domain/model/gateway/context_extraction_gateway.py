from abc import ABCMeta, abstractmethod
from typing import Optional, Dict, Any


class ContextExtractionGateway(metaclass=ABCMeta):
    """
    Gateway for extracting detailed context from security scan results.
    
    This gateway defines the contract for context extraction across different
    security scanning engines (IaC, container, dependencies, etc.).
    """
    
    @abstractmethod
    def extract_context(
        self,
        module_name: str,
        path_file_results: Optional[str],
        remote_config: Dict[str, Any],
        **kwargs
    ) -> None:
        """
        Extract context from scan results based on module type.
        
        Args:
            module_name: Name of the engine module (e.g., 'engine_iac', 'engine_container')
            path_file_results: Path to the scan results file
            remote_config: Remote configuration for the module
            **kwargs: Additional module-specific parameters
            
        Returns:
            None (prints context to stdout as per current implementation)
            
        Raises:
            FileNotFoundError: If the results file doesn't exist
            ValueError: If the results format is invalid
            Exception: For any other unexpected errors
        """
        pass
