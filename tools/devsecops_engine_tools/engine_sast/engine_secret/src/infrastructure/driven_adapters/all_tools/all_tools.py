from concurrent.futures import ThreadPoolExecutor, as_completed
from devsecops_engine_tools.engine_sast.engine_secret.src.domain.model.gateway.tool_gateway import (
    ToolGateway,
)
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings
from devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.gitleaks.gitleaks_tool import (
    GitleaksTool,
)
from devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.trufflehog.trufflehog_run import (
    TrufflehogRun,
)

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

class AllToolsSecretScan(ToolGateway):
    gitleaks_tool: GitleaksTool = GitleaksTool()
    trufflehog_tool: TrufflehogRun = TrufflehogRun()
    
    def install_tool(self, agent_os, agent_temp_dir, tool_version) -> any:
        """Install both tools in parallel"""
        gitleaks_version = tool_version.get("GITLEAKS")
        trufflehog_version = tool_version.get("TRUFFLEHOG")
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(self.gitleaks_tool.install_tool, agent_os, agent_temp_dir, gitleaks_version),
                executor.submit(self.trufflehog_tool.install_tool, agent_os, agent_temp_dir, trufflehog_version)
            ]
            
            # Esperar a que ambas completen
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error installing tool: {str(e)}")

    def run_tool_secret_scan(
        self, 
        files, 
        agent_os, 
        agent_work_folder, 
        repository_name, 
        config_tool, 
        secret_tool, 
        secret_external_checks, 
        agent_temp_dir, 
        tool, 
        folder_path
        ):
        """Run both secret scanning tools in parallel and collect their results."""
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Start both scans
            future_gitleaks = executor.submit(
                self.gitleaks_tool.run_tool_secret_scan,
                files, agent_os, agent_work_folder, repository_name, 
                config_tool, secret_tool, secret_external_checks, 
                agent_temp_dir, "gitleaks", folder_path
            )
            future_trufflehog = executor.submit(
                self.trufflehog_tool.run_tool_secret_scan,
                files, agent_os, agent_work_folder, repository_name, 
                config_tool, secret_tool, secret_external_checks, 
                agent_temp_dir, "trufflehog", folder_path
            )
            
            # Get results
            findings_gitleaks, finding_path_gitleaks = future_gitleaks.result()
            findings_trufflehog, finding_path_trufflehog = future_trufflehog.result()
        
        findings = [{"gitleaks": findings_gitleaks, "trufflehog": findings_trufflehog}]
        finding_path = finding_path_gitleaks + "#" + finding_path_trufflehog
        return findings, finding_path
