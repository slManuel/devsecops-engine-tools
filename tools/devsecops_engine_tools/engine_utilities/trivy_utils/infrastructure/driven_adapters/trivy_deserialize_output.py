from devsecops_engine_tools.engine_sca.engine_container.src.domain.model.gateways.deserealizator_gateway import (
    DeseralizatorGateway,
)
from devsecops_engine_tools.engine_core.src.domain.model.finding import (
    Finding,
    Category,
)
from devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils import (
    TrivyManagerScanUtils,
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
                        cvss=TrivyManagerScanUtils.get_cvss_v3_score(vul.get("CVSS")),
                        where=vul.get("PkgName", "")
                        + ":"
                        + vul.get("InstalledVersion", ""),
                        description=vul.get("Description", "").replace("\n", "")[:150],
                        severity=TrivyManagerScanUtils.get_cvss_v3_severity(
                            TrivyManagerScanUtils.get_cvss_v3_score(vul.get("CVSS")), 
                            vul.get("Severity", "").lower()
                        ),
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