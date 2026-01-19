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
import json
import os

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
        
        # Deduplicate: Remove TruffleHog findings that match Gitleaks findings
        try:
            # Build normalized set from Gitleaks (base de referencia)
            gitleaks_normalized = set()
            for g in findings_gitleaks or []:
                norm = self._normalize_where_from_gitleaks(g)
                if norm:
                    gitleaks_normalized.add(norm)

            # Deduplicate within TruffleHog (same filename+secret, different detectors)
            trufflehog_after_internal_dedup = self._deduplicate_trufflehog_internal(findings_trufflehog or [], folder_path)
            
            # Filter TruffleHog against Gitleaks
            filtered_trufflehog = []
            for idx, t in enumerate(trufflehog_after_internal_dedup):
                norm = self._normalize_where_from_gitleaks_against_trufflehog(t, folder_path)
                # Si la normalización coincide con Gitleaks, es un duplicado
                if norm and norm in gitleaks_normalized:
                    continue
                else:
                    filtered_trufflehog.append(t)

            findings = [{"gitleaks": findings_gitleaks, "trufflehog": filtered_trufflehog}]
            
            # Rewrite the TruffleHog findings file with only deduplicated results
            self._rewrite_trufflehog_file(filtered_trufflehog, finding_path_trufflehog)
            
        except Exception as e:
            logger.error(f"Error during deduplication: {e}")
            findings = [{"gitleaks": findings_gitleaks, "trufflehog": findings_trufflehog}]

        finding_path = finding_path_gitleaks + "#" + finding_path_trufflehog
        return findings, finding_path

    def _deduplicate_trufflehog_internal(self, findings: list, folder_path: str = "") -> list:
        """Deduplicate within TruffleHog: remove findings with same filename+secret but different detectors."""
        if not findings:
            return findings
        
        # Use filename+secret as key
        seen_by_file_secret = {}
        deduplicated = []
        
        for finding in findings:
            path = ""
            try:
                path = (
                    finding.get("SourceMetadata", {})
                    .get("Data", {})
                    .get("Filesystem", {})
                    .get("file", "")
                )
            except (AttributeError, TypeError):
                path = finding.get("file", "") or ""
            
            # Extract only filename
            filename = path.split('/')[-1] if '/' in path else path
            filename = filename.split('\\')[-1] if '\\' in filename else filename
            
            # Get the secret
            secret = finding.get("Raw") or finding.get("RawV2") or finding.get("Match") or finding.get("Redacted") or ""
            masked_secret = self._mask_secret(secret)
            
            # Key: filename + secret (without detector)
            key = f"{filename}|{masked_secret}"
            
            if key not in seen_by_file_secret:
                seen_by_file_secret[key] = True
                deduplicated.append(finding)
        
        return deduplicated

    def _normalize_where_from_gitleaks_against_trufflehog(self, item: dict, folder_path: str = "") -> str:
        """
        Normalize TruffleHog item for comparison against Gitleaks.
        Uses only filename + masked secret (no detector) to match the actual secret.
        """
        if not item:
            return ""
        
        # Extract path from nested structure
        path = ""
        try:
            path = (
                item.get("SourceMetadata", {})
                .get("Data", {})
                .get("Filesystem", {})
                .get("file", "")
            )
        except (AttributeError, TypeError):
            path = item.get("file", "") or ""
        
        # Extract only filename from path
        filename = path.split('/')[-1] if '/' in path else path
        filename = filename.split('\\')[-1] if '\\' in filename else filename
        
        # Get the secret from various possible fields
        secret = item.get("Raw") or item.get("RawV2") or item.get("Match") or item.get("Redacted") or ""
        masked = self._mask_secret(secret)
        
        # For Gitleaks comparison, use ONLY filename and secret (no detector)
        # This matches how Gitleaks reports secrets
        if not (filename or masked):
            return ""
        
        # Return a generic format that can match with Gitleaks
        normalized = f"*|{filename}|{masked}"
        return normalized.strip()

    def _rewrite_trufflehog_file(self, filtered_findings: list, file_path: str) -> None:
        """Rewrite the TruffleHog findings file with deduplicated results."""
        try:
            
            if not file_path:
                return
            
            if not os.path.exists(file_path):
                return
            
            # Write findings to file
            with open(file_path, "w") as file:
                for idx, finding in enumerate(filtered_findings):
                    json_str = json.dumps(finding)
                    file.write(json_str + '\n')
                
        except Exception as e:
            logger.error(f"Error rewriting TruffleHog file: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _mask_secret(self, secret: str) -> str:
        """Mask secret value for comparison: keep first 3 and last 3 chars"""
        if not secret:
            return ""
        secret = str(secret)
        if "*" in secret:
            return secret
        if len(secret) > 6:
            return secret[:3] + "*" * 9 + secret[-3:]
        return secret

    def _normalize_where_from_gitleaks(self, item: dict) -> str:
        """
        Normalize Gitleaks item for deduplication.
        Extracts: detector (RuleID), filename (not full path), and masked secret
        to match the normalization logic used in all_tools_deserealizator.py
        """
        if not item:
            return ""
        
        # Extract components
        path = item.get("File", "") or ""
        # Extract only filename from path (last component)
        filename = path.split('/')[-1] if '/' in path else path
        filename = filename.split('\\')[-1] if '\\' in filename else filename
        
        # Detector is typically RuleID for Gitleaks
        detector = item.get("RuleID") or ""
        
        # Get the secret
        secret = item.get("Secret") or item.get("Match") or ""
        masked = self._mask_secret(secret)
        
        # Build normalized key: detector|filename|secret (no line, no full path)
        if not (filename or detector or masked):
            return ""
        
        normalized = f"{detector}|{filename}|{masked}"
        return normalized.strip()

    def _normalize_where_from_trufflehog(self, item: dict, folder_path: str = "") -> str:
        """
        Normalize TruffleHog item for deduplication.
        Extracts: detector (ExtraData.name or DetectorName), filename, and masked secret
        to match the normalization logic used in all_tools_deserealizator.py
        """
        if not item:
            return ""
        
        # Extract path from nested structure
        path = ""
        try:
            path = (
                item.get("SourceMetadata", {})
                .get("Data", {})
                .get("Filesystem", {})
                .get("file", "")
            )
        except (AttributeError, TypeError):
            path = item.get("file", "") or ""
        
        # Extract only filename from path (last component)
        filename = path.split('/')[-1] if '/' in path else path
        filename = filename.split('\\')[-1] if '\\' in filename else filename
        
        # Detector: prefer ExtraData.name when present, otherwise use DetectorName or RuleID
        detector = (item.get("ExtraData") or {}).get("name") or item.get("DetectorName") or item.get("RuleID") or ""
        
        # Get the secret from various possible fields
        secret = item.get("Raw") or item.get("RawV2") or item.get("Match") or item.get("Redacted") or ""
        masked = self._mask_secret(secret)
        
        # Build normalized key: detector|filename|secret (no line, no full path)
        if not (filename or detector or masked):
            return ""
        
        normalized = f"{detector}|{filename}|{masked}"
        return normalized.strip()
