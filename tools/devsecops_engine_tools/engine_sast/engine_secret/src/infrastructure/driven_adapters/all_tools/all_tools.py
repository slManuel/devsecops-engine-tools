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
import re

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
        # Deduplicate TruffleHog findings against Gitleaks using normalized 'where'
        try:
            seen = set()
            for g in findings_gitleaks or []:
                seen.add(self._normalize_where_from_gitleaks(g))

            filtered_trufflehog = []
            for t in findings_trufflehog or []:
                norm = self._normalize_where_from_trufflehog(t, folder_path)
                # Only deduplicate when we have a non-empty normalized key.
                if norm and norm in seen:
                    logger.info(f"Deduplicated TruffleHog finding: {norm}")
                else:
                    filtered_trufflehog.append(t)
                    if norm:
                        seen.add(norm)

            findings = [{"gitleaks": findings_gitleaks, "trufflehog": filtered_trufflehog}]
        except Exception as e:
            logger.error(f"Error during deduplication: {e}")

        return findings, finding_path

    def _mask_secret(self, secret: str) -> str:
        if not secret:
            return ""
        secret = str(secret)
        if "*" in secret:
            return secret
        if len(secret) > 6:
            return secret[:3] + "*" * 9 + secret[-3:]
        return secret

    def _normalize_where_from_gitleaks(self, item: dict) -> str:
        # Gitleaks items typically have 'File' and 'Secret' or 'Match'
        path = item.get("File", "") or ""
        path = path.lstrip("/")
        line = item.get("StartLine") or item.get("StartColumn") or ""
        detector = item.get("RuleID") or item.get("Fingerprint") or ""
        secret = item.get("Secret") or item.get("Match") or ""
        masked = self._mask_secret(secret)

        # if we don't have meaningful identifying information, return empty to avoid spurious deduplication
        if not (path or line or detector or masked):
            return ""

        normalized = f"{path}"
        if line:
            normalized += f":{line}"
        if detector:
            normalized += f", Detector: {detector}"
        normalized += f", Secret: {masked}"
        return normalized.strip()

    def _normalize_where_from_trufflehog(self, item: dict, folder_path: str = "") -> str:
        # TruffleHog items have nested SourceMetadata -> Data -> Filesystem -> file
        path = ""
        try:
            path = (
                item.get("SourceMetadata", {})
                .get("Data", {})
                .get("Filesystem", {})
                .get("file", "")
            )
        except Exception:
            path = item.get("file", "") or ""

        # Remove provided folder_path prefix if present
        try:
            if folder_path and path.startswith(folder_path):
                path = path.replace(folder_path, "", 1)
        except Exception:
            pass

        path = path.lstrip("/")

        # secrets may be in Raw, RawV2, Match, or Redacted
        secret = item.get("Raw") or item.get("RawV2") or item.get("Match") or item.get("Redacted") or ""
        # try to extract line if present in various fields
        line = item.get("StartLine") or item.get("line") or item.get("StartColumn") or (
            item.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("line")
        )
        # prefer ExtraData.name when present, otherwise use DetectorName
        detector = (item.get("ExtraData") or {}).get("name") or item.get("DetectorName") or ""
        masked = self._mask_secret(secret)

        # avoid returning a non-informative normalized key
        if not (path or line or detector or masked):
            return ""

        normalized = f"{path}"
        if line:
            normalized += f":{line}"
        if detector:
            normalized += f", Detector: {detector}"
        normalized += f", Secret: {masked}"
        return normalized.strip()
