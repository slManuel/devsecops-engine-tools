from dataclasses import dataclass
from typing import Any, Optional

from devsecops_engine_tools.engine_utilities.azuredevops.models.AzurePredefinedVariables import (
    AgentVariables,
    SystemVariables,
    BuildVariables,
    CustomVariables,
)
from devsecops_engine_tools.engine_utilities.azuredevops.infrastructure.azure_devops_api import (
    AzureDevopsApi,
)
from devsecops_engine_tools.engine_utilities.azuredevops.models.AzureMessageLoggingPipeline import (
    AzureMessageLoggingPipeline,
)
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


@dataclass
class AzureDevops:
    use_remote_org: bool = False
    remote_org: str = ""
    remote_pat: str = ""
    remote_proj: str = ""

    def get_remote_config(self, remote_config_repo: str, remote_config_path: str) -> Any:
        """
        Lee un JSON de configuración remota (Azure DevOps Repos) usando la URL compacta.
        Respeta el modo 'use_remote_org' para apuntar a otra organización/proyecto.
        """
        if self.use_remote_org:
            org_slug = self.remote_org.rstrip("/").split("/")[-1].replace(".visualstudio.com", "")
            base_compact_remote_config_url = (
                f"https://{org_slug}.visualstudio.com/{self.remote_proj}"
                f"/_git/{remote_config_repo}?path={remote_config_path}"
            )
            pat = self.remote_pat
        else:
            org_slug = (
                SystemVariables.System_TeamFoundationCollectionUri.value()
                .rstrip("/")
                .split("/")[-1]
                .replace(".visualstudio.com", "")
            )
            base_compact_remote_config_url = (
                f"https://{org_slug}.visualstudio.com/{SystemVariables.System_TeamProject.value()}"
                f"/_git/{remote_config_repo}?path={remote_config_path}"
            )
            pat = SystemVariables.System_AccessToken.value()

        utils_azure = AzureDevopsApi(
            personal_access_token=pat,
            compact_remote_config_url=base_compact_remote_config_url,
        )
        connection = utils_azure.get_azure_connection()
        return utils_azure.get_remote_json_config(connection=connection)

    def get_variable(self, variable: str) -> Optional[str]:
        """
        Devuelve variables comunes del pipeline ADO.
        """
        try:
            if variable == "REPOSITORY":
                try:
                    pr_id = SystemVariables.System_PullRequestId.value()
                    if pr_id:
                        return CustomVariables.Custom_BvRepository_Name.value()
                    else:
                        return BuildVariables.Build_Repository_Name.value()
                except Exception:
                    return BuildVariables.Build_Repository_Name.value()

            elif variable == "BUILD_ID":
                return BuildVariables.Build_BuildId.value()
            elif variable == "PATH_DIRECTORY":
                return SystemVariables.System_DefaultWorkingDirectory.value()
            elif variable == "ACCESS_TOKEN":
                return SystemVariables.System_AccessToken.value()
            elif variable == "ORGANIZATION":
                return SystemVariables.System_TeamFoundationCollectionUri.value()
            elif variable == "PROJECT_ID":
                return SystemVariables.System_TeamProjectId.value()
            elif variable == "PR_ID":
                return SystemVariables.System_PullRequestId.value()
            elif variable == "TARGET_BRANCH":
                return SystemVariables.System_TargetBranchName.value()
            elif variable == "SOURCE_BRANCH":
                return SystemVariables.System_SourceBranch.value()
            elif variable == "OS":
                return AgentVariables.Agent_OS.value()
            elif variable == "OS_ARCHITECTURE":
                return AgentVariables.Agent_OSArchitecture.value()
            elif variable == "WORK_FOLDER":
                return AgentVariables.Agent_WorkFolder.value()
            elif variable == "TEMP_DIRECTORY":
                return AgentVariables.Agent_TempDirectory.value()
            elif variable == "TEAM_COLLECTION_URI":
                return SystemVariables.System_TeamFoundationCollectionUri.value()
            elif variable == "TEAM_PROJECT":
                return SystemVariables.System_TeamProject.value()
            elif variable == "PULL_REQUEST_ID":
                return SystemVariables.System_PullRequestId.value()

        except Exception as e:
            logger.warning(f"Error getting variable: {str(e)}")
        return None

    def message(self, type: str, message: str) -> str:
        """
        Formatea mensajes para el pipeline (##vso commands).
        """
        if type == "succeeded":
            return AzureMessageLoggingPipeline.SucceededLogging.get_message(message)
        elif type == "info":
            return AzureMessageLoggingPipeline.InfoLogging.get_message(message)
        elif type == "warning":
            return AzureMessageLoggingPipeline.WarningLogging.get_message(message)
        elif type == "error":
            return AzureMessageLoggingPipeline.ErrorLogging.get_message(message)
        else:
            # Por defecto, úsalo como info
            return AzureMessageLoggingPipeline.InfoLogging.get_message(message)
