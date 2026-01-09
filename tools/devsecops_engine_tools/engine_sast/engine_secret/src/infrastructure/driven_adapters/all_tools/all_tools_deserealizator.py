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
        Extracts: detector, filename (not full path), and secret
        to be path-agnostic and robust to different path reporting formats.
        """
        if not where:
            return ""

        # Parse the where string which is typically formatted as:
        # "path[:line], [Detector: name], [Secret|Misconfiguration]: xxx"
        detector = ""
        filename = ""
        secret = ""

        # split by commas
        pieces = [p.strip() for p in where.split(',') if p.strip()]
        
        if pieces:
            # first piece contains path and optionally line
            first = pieces[0]
            # remove leading slashes/backslashes to normalize
            path = first.split(':')[0].lstrip('/').lstrip('\\')
            # extract only filename (last component)
            filename = path.split('/')[-1] if '/' in path else path
            filename = filename.split('\\')[-1] if '\\' in filename else filename

        # extract detector and secret from remaining pieces
        for p in pieces[1:]:
            lower_p = p.lower()
            if lower_p.startswith('detector:'):
                detector = p.split(':', 1)[1].strip()
            elif lower_p.startswith('secret:'):
                secret_raw = p.split(':', 1)[1].strip()
                # extract only the masked secret value
                m = re.search(r'(\S+)', secret_raw)
                if m:
                    secret = m.group(1)
            elif lower_p.startswith('misconfiguration:'):
                secret_raw = p.split(':', 1)[1].strip()
                m = re.search(r'(\S+)', secret_raw)
                if m:
                    secret = m.group(1)

        # Build normalized key: detector|filename|secret (path-agnostic)
        if not (detector or filename or secret):
            return ""

        normalized = f"{detector}|{filename}|{secret}"
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