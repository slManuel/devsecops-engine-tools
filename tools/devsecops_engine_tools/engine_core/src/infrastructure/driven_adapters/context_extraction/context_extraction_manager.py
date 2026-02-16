from typing import Optional, Dict, Any
from devsecops_engine_tools.engine_core.src.domain.model.gateway.context_extraction_gateway import (
    ContextExtractionGateway,
)
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


class ContextExtractionManager(ContextExtractionGateway):
 
    def __init__(self):
        self._tool_gateways = {}
        
        # Mapping of module names to their tool gateway method names
        self._method_mapping = {
            "engine_iac": "get_iac_context_from_results",
            "engine_container": "get_container_context_from_results",
            "engine_dependencies": "get_dependencies_context_from_results",
        }
        
    def register_tool_gateway(self, module_name: str, tool_gateway: any):
        self._tool_gateways[module_name] = tool_gateway
        logger.info(f"Registered tool gateway for context extraction: {module_name}")
        
    def extract_context(
        self,
        module_name: str,
        path_file_results: Optional[str],
        remote_config: Dict[str, Any],
        **kwargs
    ) -> None:
        if not path_file_results:
            logger.warning(f"No results file provided for {module_name}, skipping context extraction")
            return
            
        tool_gateway = self._tool_gateways.get(module_name)
        if not tool_gateway:
            logger.warning(f"No tool gateway registered for module: {module_name}")
            return
        
        method_name = self._method_mapping.get(module_name)
        if not method_name:
            logger.warning(f"No context extraction method defined for module: {module_name}")
            return
            
        try:
            logger.info(f"Extracting context for {module_name} from {path_file_results}")
            
            # Get the method from the tool gateway
            method = getattr(tool_gateway, method_name, None)
            if not method:
                logger.error(f"Tool gateway for {module_name} does not implement {method_name}")
                return
            
            # Call the appropriate method based on module requirements
            if module_name == "engine_dependencies":
                # Dependencies requires remote_config
                method(path_file_results, remote_config=remote_config, **kwargs)
            else:
                # IaC and Container only need path_file_results
                method(path_file_results)
            
            logger.info(f"Context extraction completed for {module_name}")
        except FileNotFoundError as e:
            logger.error(f"Results file not found for {module_name}: {path_file_results}")
        except ValueError as e:
            logger.error(f"Invalid results format for {module_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error extracting context for {module_name}: {str(e)}")
