from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List
from devsecops_engine_tools.engine_core.src.domain.model.finding import Finding
from devsecops_engine_tools.engine_sast.engine_secret.src.domain.model.gateway.gateway_deserealizator import (
    DeseralizatorGateway
)
from devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.gitleaks.gitleaks_deserealizator import (
    GitleaksDeserealizator
)
from devsecops_engine_tools.engine_sast.engine_secret.src.infrastructure.driven_adapters.trufflehog.trufflehog_deserealizator import (
    SecretScanDeserealizator
)

@dataclass
class AllToolsSecretScanDeserealizator(DeseralizatorGateway):
    gitleaks_deserealizator: GitleaksDeserealizator = field(default_factory=GitleaksDeserealizator)
    trufflehog_deserealizator: SecretScanDeserealizator = field(default_factory=SecretScanDeserealizator)

    def get_list_vulnerability(
        self, 
        results_scan_list: List[dict], 
        path_directory: str, 
        os: str
        ) -> List[Finding]:
        list_open_vulnerabilities = []
        all_results = results_scan_list[0]
        findings_gitleaks = all_results.get("gitleaks", [])
        findings_trufflehog = all_results.get("trufflehog", [])
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_gitleaks = executor.submit(
                self.gitleaks_deserealizator.get_list_vulnerability,
                findings_gitleaks, path_directory, os
            )
            future_trufflehog = executor.submit(
                self.trufflehog_deserealizator.get_list_vulnerability,
                findings_trufflehog, os, path_directory
            )
            list_open_gitleaks = future_gitleaks.result()
            list_open_trufflehog = future_trufflehog.result()
        
        # Add all Gitleaks vulnerabilities first (priority)
        list_open_vulnerabilities.extend(list_open_gitleaks)
        
        # Create set of unique keys from Gitleaks findings based on normalized 'where' field
        seen_findings = {self._normalize_where(finding.where) for finding in list_open_gitleaks}
        
        # Add only TruffleHog vulnerabilities that are not duplicates
        for finding in list_open_trufflehog:
            normalized_where = self._normalize_where(finding.where)
            if normalized_where not in seen_findings:
                list_open_vulnerabilities.append(finding)
                seen_findings.add(normalized_where)

        return list_open_vulnerabilities
    
    def _normalize_where(self, where: str) -> str:
        """
        Normalize the 'where' field to enable proper deduplication.
        Handles differences in path formatting between Gitleaks and TruffleHog.
        
        Examples:
            - "config.py, Secret: xox*********5t6" -> "config.py, Secret: xox*********5t6"
            - "/config.py, Secret: xox*********5t6" -> "config.py, Secret: xox*********5t6"
        """
        # Remove leading slash from path if present
        if where.startswith("/"):
            where = where[1:]
        return where
    
    def get_where_correctly(self, result: dict, path_directory=""):
        path = result.get("File", "").replace(path_directory, "")
        hidden_secret = str(result.get("Secret"))[:3] + '*' * 9 + str(result.get("Secret"))[-3:]
        return f"{path}, Secret: {hidden_secret}"