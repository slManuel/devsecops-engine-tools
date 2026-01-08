import re
from datetime import datetime
from dataclasses import dataclass
from typing import List
from devsecops_engine_tools.engine_core.src.domain.model.finding import Finding, Category
from devsecops_engine_tools.engine_sast.engine_secret.src.domain.model.gateway.gateway_deserealizator import DeseralizatorGateway
import re

@dataclass
class SecretScanDeserealizator(DeseralizatorGateway):

    def get_list_vulnerability(self, results_scan_list: List[dict], os, path_directory) -> List[Finding]:
        list_open_vulnerabilities = []
        current_date=datetime.now().strftime("%d%m%Y")

        for result in results_scan_list:
            where_text, raw_data = self.get_where_correctly(result, os, path_directory)
            rule_name = result.get("Id", "")

            # determine detector/requirement separately
            # prefer DetectorName when present (test expectations), otherwise ExtraData.name or RuleID
            detector_name = result.get("DetectorName") or (result.get("ExtraData") or {}).get("name") or result.get("RuleID") or ""

            if "MISCONFIGURATION_SCANNING" in rule_name:
                description = "Actuator misconfiguration can leak sensitive information"
                where = f"{where_text}, Misconfiguration: {raw_data}"
            else:
                description = "Sensitive information in source code"
                where = f"{where_text}, Secret: {raw_data}"

            vulnerability_open = Finding(
                id=result.get("Id", ""),
                cvss=None,
                where=where,
                description=description,
                severity="critical",
                identification_date=current_date,
                published_date_cve=None,
                module="engine_secret",
                category=Category.VULNERABILITY,
                requirements=detector_name,
                tool="Trufflehog",
            )
            list_open_vulnerabilities.append(vulnerability_open)
        return list_open_vulnerabilities
    
    def get_where_correctly(self, result: dict, os, path_directory):
        """
        Return (where_path_with_leading_sep, masked_secret)
        This function keeps backward-compatible output shape for tests and callers.
        """
        # Extract path/file
        full_path = ""
        try:
            full_path = str(result.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("file", "") or "")
        except Exception:
            full_path = ""

        if not full_path:
            full_path = str(result.get("File") or "")

        # Normalize path separators for Linux-like OS strings
        if re.search(r'Linux', str(os)):
            full_path = full_path.replace("\\", "/")

        path_remove = path_directory or ""
        where_path = full_path.replace(path_remove, "")

        # keep leading slash/backslash as original behavior expected by tests

        # mask raw/secret
        secret_raw = str(result.get("Raw") or result.get("Match") or result.get("Redacted") or "")
        if secret_raw:
            if '*' in secret_raw:
                hidden = secret_raw
            else:
                hidden = (secret_raw[:3] + ('*' * 9) + secret_raw[-3:]) if len(secret_raw) >= 6 else secret_raw
        else:
            hidden = ''

        return where_path, hidden