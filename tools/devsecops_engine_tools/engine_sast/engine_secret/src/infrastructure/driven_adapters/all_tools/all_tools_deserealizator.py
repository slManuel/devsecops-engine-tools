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

        # Expect formats like:
        # - "path, Secret: xxx"
        # - "path:line, Detector: name, Secret: xxx"
        # We will extract path, optional line, optional detector, and secret.
        path_part = ''
        line_part = ''
        detector_part = ''
        secret_part = ''

        # split by commas but keep parts manageable
        pieces = [p.strip() for p in where.split(',') if p.strip()]
        if pieces:
            # first piece may contain path or path:line
            first = pieces[0]
            if ':' in first and not first.lower().startswith('secret'):
                # path:line
                idx = first.rfind(':')
                path_part = first[:idx].lstrip('/')
                line_part = first[idx+1:]
            else:
                path_part = first.lstrip('/')

        for p in pieces[1:]:
            if p.lower().startswith('detector:'):
                detector_part = p.split(':',1)[1].strip()
            elif p.lower().startswith('secret:'):
                secret_part = p.split(':',1)[1].strip()
            else:
                # fallback: could be ExtraData name or other
                if not detector_part:
                    detector_part = p

        # Normalize secret mask
        if secret_part:
            m = re.search(r"(\S+)", secret_part)
            if m:
                secret_raw = m.group(1)
                if '*' in secret_raw:
                    masked = secret_raw
                else:
                    masked = (secret_raw[:3] + '*' * 9 + secret_raw[-3:]) if len(secret_raw) > 6 else secret_raw
                secret_part = masked

        normalized = f"{path_part}"
        if line_part:
            normalized += f":{line_part}"
        if detector_part:
            normalized += f", Detector: {detector_part}"
        if secret_part:
            normalized += f", Secret: {secret_part}"

        return normalized.strip()
    
    def get_where_correctly(self, result: dict, path_directory=""):
        # Build a more detailed where string including line and detector/extra name
        full_path = result.get("File", "") or ""
        # Try trufflehog style nested path
        if not full_path:
            try:
                full_path = (
                    result.get("SourceMetadata", {})
                    .get("Data", {})
                    .get("Filesystem", {})
                    .get("file", "")
                )
            except Exception:
                full_path = full_path

        # Remove path_directory prefix
        try:
            relative = full_path.replace(path_directory, "") if path_directory else full_path
        except Exception:
            relative = full_path
        path = relative.lstrip('/')

        # extract line if available
        line = result.get("StartLine") or result.get("line") or (
            result.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("line")
        )

        # prefer ExtraData.name when present, otherwise use DetectorName or RuleID
        detector = (result.get("ExtraData") or {}).get("name") or result.get("DetectorName") or result.get("RuleID") or ""

        secret = str(result.get("Secret", "") or result.get("Match", "") or result.get("Raw", "") or result.get("RawV2", "") or result.get("Redacted", ""))
        if '*' in secret:
            hidden_secret = secret
        else:
            hidden_secret = (secret[:3] + '*' * 9 + secret[-3:]) if len(secret) > 6 else secret

        where = f"{path}"
        if line:
            where += f":{line}"
        if detector:
            where += f", Detector: {detector}"
        where += f", Secret: {hidden_secret}"

        return where