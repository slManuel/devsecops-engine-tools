from dataclasses import dataclass
from devsecops_engine_tools.engine_core.src.domain.model.gateway.risk_score_gateway import (
    RiskScoreGateway,
)
from devsecops_engine_tools.engine_core.src.domain.model.finding import Priority
import re
import requests

from devsecops_engine_tools.engine_utilities import settings
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


@dataclass
class RiskScore(RiskScoreGateway):
    def get_risk_score(self, finding_list, config_tool):
        priority_manager = config_tool.get("PRIORITY_MANAGER", {})
        mapping_to_host = priority_manager.get("MAPPING_HOST", {})
        if priority_manager.get("USE_PRIORITY", False):
            cve_regex = re.compile(priority_manager.get("CVE_REGEX"))
            cve_findings = [f for f in finding_list if cve_regex.match(f.id)]
            non_cve_findings = [f for f in finding_list if not cve_regex.match(f.id)]

            if cve_findings:
                host = priority_manager.get("HOST_PRIORITY")
                ids = [f.id for f in cve_findings]
                cve_list_header = ",".join(ids)
                try:
                    response = requests.get(
                        host,
                        headers={"cve_list": cve_list_header},
                        timeout=10
                    )
                    response.raise_for_status()
                    priorities = response.json().get("priorities", {})
                    
                    for finding in cve_findings:
                        prio = priorities.get(finding.id)
                        if prio:
                            finding.priority = Priority(
                                score=float(prio.get("priority", 0.0)), 
                                scale=mapping_to_host.get(prio.get("classification", "Unknown"))
                            )
                        else:
                            finding.priority = self._homologate_priority_by_severity(
                                finding.severity, 
                                priority_manager.get("HOMOLOGATION_PRIORITY", {})
                            )
                except Exception as e:
                    logger.error(f"Error al consultar prioridades externas: {e}")
                    for finding in cve_findings:
                        finding.priority = self._homologate_priority_by_severity(
                            finding.severity, 
                            priority_manager.get("HOMOLOGATION_PRIORITY", {})
                        )


            for finding in non_cve_findings:
                finding.priority = self._homologate_priority_by_severity(
                    finding.severity, 
                    priority_manager.get("HOMOLOGATION_PRIORITY", {})
                    )

    def _homologate_priority_by_severity(self, severity, homologation_config):
        if severity in homologation_config:
            conf = homologation_config[severity]
            return Priority(score=conf.get("SCORE", 0.0), scale=conf.get("CLASSIFICATION", "Unknown"))
        return Priority(score=0.0, scale="Unknown")


