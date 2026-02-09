from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities.settings import SETTING_LOGGER

logger = MyLogger.__call__(**SETTING_LOGGER).get_logger()


class AzurePipelineVariableAdapter:
   
    @staticmethod
    def set_variable(variable_name: str, variable_value: str, is_secret: bool = False) -> None:
        
        if not variable_name or not isinstance(variable_name, str):
            raise ValueError("El nombre de la variable debe ser una cadena no vacía")
        
        if not isinstance(variable_value, str):
            variable_value = str(variable_value)

        # Comando de Azure DevOps para establecer una variable
        secret_flag = ";issecret=true" if is_secret else ""
        command = f"##vso[task.setvariable variable={variable_name}{secret_flag}]{variable_value}"
        
        print(command)
        logger.info(f"Variable '{variable_name}' establecida en el pipeline de Azure DevOps")

   