from datetime import datetime
from typing import Dict, Any, List

from devsecops_engine_tools.engine_core.src.domain.model.finding import Category, EngineCodeFinding


class KiuwanDeserealizator:
    
    """
        This class has the functions to deserealize the defects found in kiuwan analysis scan.
    """
    
    @staticmethod
    def get_findings(
        last_analysis: Dict[str, Any],
        defects_data: Dict[str, Any],
        analysis_code: str,
        severity_mapper: Dict[str,str],
    ) -> List[EngineCodeFinding]:
        """
        Map Kiuwan defects to KiuwanFinding objects.

        Args:
            last_analysis: Dictionary containing the last analysis data.
            defects_data: Dictionary containing the defects data.
            analysis_code: The code of the analysis.

        Returns:
            List of KiuwanFinding objects representing the mapped defects.
        """
        analysis_date = last_analysis.get("date", datetime.now().strftime("%d/%m/%Y"))
        application_business_value = last_analysis.get("applicationBusinessValue", "")
        
        findings = []
        for defect in defects_data.get("defects", []):
            # Mapear characteristic a Category
            characteristic = defect.get("characteristic", "").lower()
           
            finding = EngineCodeFinding(
                id=str(defect.get("defectId", "")),
                cvss=defect.get("ruleCode", ""),
                where=f"{defect.get('file', '')}:{defect.get('line', '')}",
                description=defect.get("rule", ""),
                severity=severity_mapper.get(defect.get("priority", ""), "Undefined"),
                identification_date=analysis_date,
                published_date_cve="",
                module="engine_code",
                category=Category.VULNERABILITY if characteristic == "security" else Category.COMPLIANCE,
                requirements="",
                tool="kiuwan",
                analysis_url=last_analysis.get("analysisURL", "No available"),
                analysis_code=analysis_code,
                label=defect.get("label", ""),
                application_business_value=application_business_value,
                defect_type=characteristic
            )
            findings.append(finding)
        
        return findings