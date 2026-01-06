from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
import os
import re
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
        if not where:
            return ""

        parts = where.split(',', 1)
        path_part = parts[0].lstrip('/')

        # Use basename so differences in parent paths don't prevent deduplication
        path_base = os.path.basename(path_part)

        rest = parts[1] if len(parts) > 1 else ''

        # Normalize secret mask so different masking styles still match
        m = re.search(r'Secret:\s*(\S+)', rest)
        if m:
            secret_raw = m.group(1)
            if '*' in secret_raw:
                masked = secret_raw
            else:
                # keep first 3 and last 3 if possible, otherwise keep original
                masked = (secret_raw[:3] + '*' * 9 + secret_raw[-3:]) if len(secret_raw) > 6 else secret_raw
            rest = f', Secret: {masked}'

        normalized = f"{path_base}{rest}".strip()
        return normalized
    
    def get_where_correctly(self, result: dict, path_directory=""):
        full_path = result.get("File", "")
        # Remove path_directory if present, then use basename for consistent output
        try:
            relative = full_path.replace(path_directory, "") if path_directory else full_path
        except Exception:
            relative = full_path
        path = os.path.basename(relative.lstrip('/'))

        secret = str(result.get("Secret", ""))
        if '*' in secret:
            hidden_secret = secret
        else:
            hidden_secret = (secret[:3] + '*' * 9 + secret[-3:]) if len(secret) > 6 else secret

        return f"{path}, Secret: {hidden_secret}"