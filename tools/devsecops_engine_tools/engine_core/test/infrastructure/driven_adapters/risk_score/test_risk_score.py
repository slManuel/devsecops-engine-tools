import unittest
from unittest.mock import Mock, patch, MagicMock
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.risk_score.risk_score import RiskScore
from devsecops_engine_tools.engine_core.src.domain.model.finding import Finding, Priority, Category


class TestRiskScore(unittest.TestCase):

    def setUp(self):
        self.risk_score = RiskScore()
        self.config_tool = {
            "PRIORITY_MANAGER": {
                "USE_PRIORITY": True,
                "CVE_REGEX": r"CVE-\d{4}-\d+",
                "HOST_PRIORITY": "https://api.example.com/priority",
                "MAPPING_HOST": {
                    "critical": "Very Critical",
                    "high": "Critical",
                    "medium": "High",
                    "low": "Medium-Low"
                },
                "HOMOLOGATION_PRIORITY": {
                    "Critical": {
                        "SCORE": 1.00,
                        "CLASSIFICATION": "Very Critical"
                    },
                    "High": {
                        "SCORE": 0.74,
                        "CLASSIFICATION": "Critical"
                    },
                    "Medium": {
                        "SCORE": 0.46,
                        "CLASSIFICATION": "High"
                    },
                    "Low": {
                        "SCORE": 0.01,
                        "CLASSIFICATION": "Medium-Low"
                    }
                }
            }
        }

    def _create_finding(self, id, severity="High", category=Category.VULNERABILITY):
        return Finding(
            id=id,
            cvss="7.5",
            where="/path/to/file",
            description="Test vulnerability",
            severity=severity,
            identification_date="2025-01-01",
            published_date_cve="2025-01-01",
            module="engine_dependencies",
            category=category,
            requirements="",
            tool="trivy"
        )

    def test_use_priority_disabled(self):
        """Test cuando USE_PRIORITY es False"""
        config = {"PRIORITY_MANAGER": {"USE_PRIORITY": False}}
        findings = [self._create_finding("CVE-2024-12345")]
        
        self.risk_score.get_risk_score(findings, config)
        
        # No se debe asignar priority cuando está deshabilitado
        self.assertIsNone(findings[0].priority)

    def test_non_cve_findings_homologation(self):
        """Test homologación de findings sin formato CVE"""
        findings = [
            self._create_finding("VULN-001", "Critical"),
            self._create_finding("VULN-002", "High"),
            self._create_finding("VULN-003", "Medium"),
            self._create_finding("VULN-004", "Low")
        ]
        
        self.risk_score.get_risk_score(findings, self.config_tool)
        
        # Verificar que se asigna priority por homologación
        self.assertIsNotNone(findings[0].priority)
        self.assertEqual(findings[0].priority.score, 1.00)
        self.assertEqual(findings[0].priority.scale, "Very Critical")
        
        self.assertEqual(findings[1].priority.score, 0.74)
        self.assertEqual(findings[1].priority.scale, "Critical")
        
        self.assertEqual(findings[2].priority.score, 0.46)
        self.assertEqual(findings[2].priority.scale, "High")
        
        self.assertEqual(findings[3].priority.score, 0.01)
        self.assertEqual(findings[3].priority.scale, "Medium-Low")

    @patch('devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.risk_score.risk_score.requests.get')
    def test_cve_findings_with_api_response(self, mock_get):
        """Test CVE findings con respuesta exitosa del API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "priorities": {
                "CVE-2024-12345": {
                    "priority": "3.9",
                    "classification": "critical"
                },
                "CVE-2025-1345": {
                    "priority": "2.5",
                    "classification": "medium"
                }
            }
        }
        mock_get.return_value = mock_response
        
        findings = [
            self._create_finding("CVE-2024-12345", "High"),
            self._create_finding("CVE-2025-1345", "Medium")
        ]
        
        self.risk_score.get_risk_score(findings, self.config_tool)
        
        # Verificar que se llamó al API con los headers correctos
        mock_get.assert_called_once_with(
            "https://api.example.com/priority",
            headers={"cve_list": "CVE-2024-12345,CVE-2025-1345"},
            timeout=10
        )
        
        # Verificar que se asignó priority desde la respuesta del API
        self.assertIsNotNone(findings[0].priority)
        self.assertEqual(findings[0].priority.score, 3.9)
        self.assertEqual(findings[0].priority.scale, "Very Critical")
        
        self.assertEqual(findings[1].priority.score, 2.5)
        self.assertEqual(findings[1].priority.scale, "High")

    @patch('devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.risk_score.risk_score.requests.get')
    def test_cve_findings_partial_api_response(self, mock_get):
        """Test CVE findings cuando solo algunos están en la respuesta del API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "priorities": {
                "CVE-2024-12345": {
                    "priority": "3.9",
                    "classification": "critical"
                }
                # CVE-2025-1345 no está en la respuesta
            }
        }
        mock_get.return_value = mock_response
        
        findings = [
            self._create_finding("CVE-2024-12345", "High"),
            self._create_finding("CVE-2025-1345", "Medium")
        ]
        
        self.risk_score.get_risk_score(findings, self.config_tool)
        
        # CVE-2024-12345 debe tener priority del API
        self.assertEqual(findings[0].priority.score, 3.9)
        self.assertEqual(findings[0].priority.scale, "Very Critical")
        
        # CVE-2025-1345 debe usar homologación por severidad
        self.assertEqual(findings[1].priority.score, 0.46)
        self.assertEqual(findings[1].priority.scale, "High")

    @patch('devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.risk_score.risk_score.requests.get')
    def test_cve_findings_api_error(self, mock_get):
        """Test CVE findings cuando el API falla"""
        mock_get.side_effect = Exception("API connection error")
        
        findings = [
            self._create_finding("CVE-2024-12345", "Critical"),
            self._create_finding("CVE-2025-1345", "High")
        ]
        
        self.risk_score.get_risk_score(findings, self.config_tool)
        
        # Debe usar homologación por severidad cuando falla el API
        self.assertIsNotNone(findings[0].priority)
        self.assertEqual(findings[0].priority.score, 1.00)
        self.assertEqual(findings[0].priority.scale, "Very Critical")
        
        self.assertEqual(findings[1].priority.score, 0.74)
        self.assertEqual(findings[1].priority.scale, "Critical")

    @patch('devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.risk_score.risk_score.requests.get')
    def test_mixed_cve_and_non_cve_findings(self, mock_get):
        """Test con mezcla de CVE y no-CVE findings"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "priorities": {
                "CVE-2024-12345": {
                    "priority": "4.2",
                    "classification": "high"
                }
            }
        }
        mock_get.return_value = mock_response
        
        findings = [
            self._create_finding("CVE-2024-12345", "High"),
            self._create_finding("VULN-001", "Critical"),
            self._create_finding("CVE-2025-9999", "Medium")
        ]
        
        self.risk_score.get_risk_score(findings, self.config_tool)
        
        # CVE-2024-12345 desde API
        self.assertEqual(findings[0].priority.score, 4.2)
        self.assertEqual(findings[0].priority.scale, "Critical")
        
        # VULN-001 homologado por severidad
        self.assertEqual(findings[1].priority.score, 1.00)
        self.assertEqual(findings[1].priority.scale, "Very Critical")
        
        # CVE-2025-9999 no en respuesta, homologado por severidad
        self.assertEqual(findings[2].priority.score, 0.46)
        self.assertEqual(findings[2].priority.scale, "High")

    def test_homologate_priority_unknown_severity(self):
        """Test homologación con severidad desconocida"""
        priority = self.risk_score._homologate_priority_by_severity(
            "Unknown", 
            self.config_tool["PRIORITY_MANAGER"]["HOMOLOGATION_PRIORITY"]
        )
        
        self.assertEqual(priority.score, 0.0)
        self.assertEqual(priority.scale, "Unknown")

    @patch('devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.risk_score.risk_score.requests.get')
    def test_cve_regex_matching(self, mock_get):
        """Test que el regex de CVE funciona correctamente"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"priorities": {}}
        mock_get.return_value = mock_response
        
        findings = [
            self._create_finding("CVE-2024-12345", "High"),  # Debe coincidir
            self._create_finding("CVE-2025-1", "High"),       # Debe coincidir
            self._create_finding("cve-2024-12345", "High"),   # No debe coincidir (minúsculas)
            self._create_finding("VULN-CVE-2024", "High")     # No debe coincidir
        ]
        
        self.risk_score.get_risk_score(findings, self.config_tool)
        
        # Solo los 2 primeros deben intentar usar el API
        call_args = mock_get.call_args
        if call_args:
            headers = call_args[1].get('headers', {})
            cve_list = headers.get('cve_list', '')
            cve_count = len(cve_list.split(',')) if cve_list else 0
            self.assertEqual(cve_count, 2)

    def test_empty_findings_list(self):
        """Test con lista de findings vacía"""
        findings = []
        
        # No debe lanzar excepciones
        self.risk_score.get_risk_score(findings, self.config_tool)
        
        self.assertEqual(len(findings), 0)

    @patch('devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.risk_score.risk_score.requests.get')
    def test_api_timeout(self, mock_get):
        """Test cuando el API excede el timeout"""
        mock_get.side_effect = Exception("Timeout error")
        
        findings = [self._create_finding("CVE-2024-12345", "High")]
        
        self.risk_score.get_risk_score(findings, self.config_tool)
        
        # Debe usar homologación por severidad
        self.assertIsNotNone(findings[0].priority)
        self.assertEqual(findings[0].priority.score, 0.74)
        self.assertEqual(findings[0].priority.scale, "Critical")


if __name__ == '__main__':
    unittest.main()
