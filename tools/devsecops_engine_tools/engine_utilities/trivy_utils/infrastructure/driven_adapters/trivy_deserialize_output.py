from devsecops_engine_tools.engine_sca.engine_container.src.domain.model.gateways.deserealizator_gateway import (
    DeseralizatorGateway,
)
from devsecops_engine_tools.engine_core.src.domain.model.finding import (
    Finding,
    Category,
)
from dataclasses import dataclass
import json
from datetime import datetime, timezone


@dataclass
class TrivyDeserializator(DeseralizatorGateway):

    def get_list_findings(self, image_scanned, remote_config={}, module="") -> "list[Finding]":
        list_open_vulnerabilities = []
        with open(image_scanned, "rb") as file:
            image_object = file.read()
            json_data = json.loads(image_object)
            results = json_data.get("Results", [{}])

            for result in results:
                vulnerabilities_data = result.get("Vulnerabilities", [])
                vulnerabilities = [
                    Finding(
                        id=vul.get("VulnerabilityID", ""),
                        cvss=self._get_cvss_v3_score(vul.get("CVSS")),
                        where=vul.get("PkgName", "")
                        + ":"
                        + vul.get("InstalledVersion", ""),
                        description=vul.get("Description", "").replace("\n", "")[:150],
                        severity=self._get_cvss_v3_severity(self._get_cvss_v3_score(vul.get("CVSS")), vul.get("Severity", "").lower()),
                        identification_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
                        published_date_cve=self._check_date_format(vul) if vul.get("PublishedDate") else None,
                        module=module,
                        category=Category.VULNERABILITY,
                        requirements=vul.get("FixedVersion") or vul.get("Status", ""),
                        tool="Trivy",
                    )
                    for vul in vulnerabilities_data
                    
                ]
                list_open_vulnerabilities.extend(vulnerabilities)

        return list_open_vulnerabilities

    def _check_date_format(self, vul):
        try:
            published_date_cve = (
                datetime.strptime(vul.get("PublishedDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
                .replace(tzinfo=timezone.utc)
                .isoformat()
            )
        except:
            published_date_cve = (
                datetime.strptime(vul.get("PublishedDate"), "%Y-%m-%dT%H:%M:%SZ")
                .replace(tzinfo=timezone.utc)
                .isoformat()
            )
        return published_date_cve

    def _get_cvss_v3_severity(self, cvss_score: str, severity: str) -> str:
        if not cvss_score:
            severity
            return severity
        else:
            try:
                cvss_score = float(cvss_score)
            except ValueError:
                return severity
            if cvss_score < 4.0:
                return "low"
            elif 4.0 <= cvss_score < 7.0:
                return "medium"
            elif 7.0 <= cvss_score < 9.0:
                return "high"
            elif cvss_score >= 9.0:
                return "critical"
    
    def _get_cvss_v3_score(self, cvss_data: any) -> str:
        if not cvss_data:
            return ""
        else:
            return str(
                next(
                    (
                        v["V3Score"]
                        for v in cvss_data.values()
                        if "V3Score" in v
                    ),
                    "",
                )
            )