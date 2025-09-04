import unittest
import json
from unittest.mock import patch, Mock, mock_open
from devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan import TrivyScanSBOM
from devsecops_engine_tools.engine_sca.engine_dependencies.src.domain.model.context_dependencies import ContextDependencies


class TestTrivyScanSBOM(unittest.TestCase):

    def setUp(self):
        self.trivy_scanner = TrivyScanSBOM()
        self.sample_sbom_path = "/tmp/test_pipeline_SBOM.json"
        self.sample_result_path = "/tmp/test_pipeline_SBOM_scan_result.json"
        
        # Mock data for tests
        self.mock_remote_config = {
            "TRIVY": {
                "CLI_VERSION": "0.45.0"
            }
        }
        
        self.mock_trivy_result = {
            "Results": [
                {
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2021-12345",
                            "Severity": "HIGH",
                            "PkgID": "package@1.0.0",
                            "PkgName": "test-package",
                            "InstalledVersion": "1.0.0",
                            "FixedVersion": "1.0.1, 1.0.2",
                            "Description": "Test vulnerability description\nwith newlines",
                            "References": ["https://example.com/cve-2021-12345"]
                        },
                        {
                            "VulnerabilityID": "CVE-2021-67890",
                            "Severity": "MEDIUM",
                            "PkgID": "another-package@2.0.0",
                            "PkgName": "another-package",
                            "InstalledVersion": "2.0.0",
                            "FixedVersion": "2.1.0",
                            "Description": "Another test vulnerability",
                            "References": ["https://example.com/cve-2021-67890"]
                        }
                    ]
                }
            ]
        }

    @patch('devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.subprocess.run')
    def test_scan_dependencies_sbom_success(self, mock_subprocess_run):
        # Arrange
        command_prefix = "/usr/bin/trivy"
        sbom_path = self.sample_sbom_path
        expected_result_file = self.sample_result_path
        
        mock_subprocess_run.return_value = Mock(returncode=0)
        
        # Act
        with patch('builtins.print') as mock_print:
            result = self.trivy_scanner.scan_dependencies_sbom(command_prefix, sbom_path)
        
        # Assert
        self.assertEqual(result, expected_result_file)
        mock_subprocess_run.assert_called_once_with(
            [command_prefix, "sbom", sbom_path, "-f", "json", "--scanners", "vuln", "-o", expected_result_file],
            check=True,
            stdout=unittest.mock.ANY,
            stderr=unittest.mock.ANY,
            text=True
        )
        mock_print.assert_called_once_with(f"The SBOM {sbom_path} was scanned")

    @patch('devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.logger')
    @patch('devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.subprocess.run')
    def test_scan_dependencies_sbom_failure(self, mock_subprocess_run, mock_logger):
        # Arrange
        command_prefix = "/usr/bin/trivy"
        sbom_path = self.sample_sbom_path
        error_message = "Command failed"
        
        mock_subprocess_run.side_effect = Exception(error_message)
        
        # Act
        result = self.trivy_scanner.scan_dependencies_sbom(command_prefix, sbom_path)
        
        # Assert
        self.assertIsNone(result)
        mock_logger.error.assert_called_once_with(f"Error during SBOM scan of {sbom_path}: {error_message}")

    @patch('devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.os.path.exists')
    @patch('devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.TrivyScan')
    def test_run_tool_dependencies_sca_success(self, mock_trivy_scan_class, mock_exists):
        # Arrange
        mock_trivy_scan_instance = Mock()
        mock_trivy_scan_instance.identify_os_and_install.return_value = "/usr/bin/trivy"
        mock_trivy_scan_class.return_value = mock_trivy_scan_instance
        
        mock_exists.return_value = True
        
        dict_args = {}
        exclusion = []
        pipeline_name = "test_pipeline"
        to_scan = []
        secret_tool = None
        token_engine_dependencies = "test_token"
        
        expected_result_file = f"{pipeline_name}_SBOM_scan_result.json"
        
        # Act
        with patch.object(self.trivy_scanner, 'scan_dependencies_sbom', return_value=expected_result_file) as mock_scan:
            result = self.trivy_scanner.run_tool_dependencies_sca(
                self.mock_remote_config,
                dict_args,
                exclusion,
                pipeline_name,
                to_scan,
                secret_tool,
                token_engine_dependencies
            )
        
        # Assert
        self.assertEqual(result, expected_result_file)
        mock_trivy_scan_instance.identify_os_and_install.assert_called_once_with("0.45.0")
        mock_scan.assert_called_once_with("/usr/bin/trivy", f"{pipeline_name}_SBOM.json")

    @patch('devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.os.path.exists')
    @patch('devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.TrivyScan')
    def test_run_tool_dependencies_sca_no_command_prefix(self, mock_trivy_scan_class, mock_exists):
        # Arrange
        mock_trivy_scan_instance = Mock()
        mock_trivy_scan_instance.identify_os_and_install.return_value = None
        mock_trivy_scan_class.return_value = mock_trivy_scan_instance
        
        dict_args = {}
        exclusion = []
        pipeline_name = "test_pipeline"
        to_scan = []
        secret_tool = None
        token_engine_dependencies = "test_token"
        
        # Act
        result = self.trivy_scanner.run_tool_dependencies_sca(
            self.mock_remote_config,
            dict_args,
            exclusion,
            pipeline_name,
            to_scan,
            secret_tool,
            token_engine_dependencies
        )
        
        # Assert
        self.assertIsNone(result)

    @patch('devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.os.path.exists')
    @patch('devsecops_engine_tools.engine_sca.engine_dependencies.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.TrivyScan')
    def test_run_tool_dependencies_sca_sbom_not_found(self, mock_trivy_scan_class, mock_exists):
        # Arrange
        mock_trivy_scan_instance = Mock()
        mock_trivy_scan_instance.identify_os_and_install.return_value = "/usr/bin/trivy"
        mock_trivy_scan_class.return_value = mock_trivy_scan_instance
        
        mock_exists.return_value = False
        
        dict_args = {}
        exclusion = []
        pipeline_name = "test_pipeline"
        to_scan = []
        secret_tool = None
        token_engine_dependencies = "test_token"
        
        # Act & Assert
        with self.assertRaises(FileNotFoundError) as context:
            self.trivy_scanner.run_tool_dependencies_sca(
                self.mock_remote_config,
                dict_args,
                exclusion,
                pipeline_name,
                to_scan,
                secret_tool,
                token_engine_dependencies
            )
        
        self.assertEqual(str(context.exception), "SBOM file not found, enable SBOM generation to scan with Trivy.")

    def test_get_dependencies_context_from_results_success(self):
        # Arrange
        mock_file_content = json.dumps(self.mock_trivy_result).encode()
        expected_contexts_count = 2
        
        # Act
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('builtins.print') as mock_print:
                self.trivy_scanner.get_dependencies_context_from_results(
                    self.sample_result_path,
                    self.mock_remote_config
                )
        
        # Assert - verificar que se llamó print con los mensajes esperados
        print_calls = mock_print.call_args_list
        self.assertEqual(len(print_calls), 3)  # BEGIN, JSON content, END
        
        # Verificar que los prints contienen el contenido esperado
        begin_call = str(print_calls[0])
        end_call = str(print_calls[2])
        json_call = str(print_calls[1])
        
        self.assertIn("BEGIN CONTEXT OUTPUT", begin_call)
        self.assertIn("END CONTEXT OUTPUT", end_call)
        self.assertIn("dependencies_context", json_call)

    def test_get_dependencies_context_from_results_with_context_creation(self):
        # Arrange
        mock_file_content = json.dumps(self.mock_trivy_result).encode()
        
        # Act
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('builtins.print') as mock_print:
                self.trivy_scanner.get_dependencies_context_from_results(
                    self.sample_result_path,
                    self.mock_remote_config
                )
        
        # Assert - verificar el contenido del JSON impreso
        json_call_args = mock_print.call_args_list[1][0][0]
        parsed_json = json.loads(json_call_args)
        
        self.assertIn("dependencies_context", parsed_json)
        contexts = parsed_json["dependencies_context"]
        self.assertEqual(len(contexts), 2)
        
        # Verificar el primer contexto
        first_context = contexts[0]
        self.assertEqual(first_context["cve_id"], ["CVE-2021-12345"])
        self.assertEqual(first_context["severity"], "high")
        self.assertEqual(first_context["component"], "package@1.0.0")
        self.assertEqual(first_context["package_name"], "test-package")
        self.assertEqual(first_context["installed_version"], "1.0.0")
        self.assertEqual(first_context["fixed_version"], ["1.0.1", "1.0.2"])
        self.assertEqual(first_context["description"], "Test vulnerability descriptionwith newlines")
        self.assertEqual(first_context["source_tool"], "Trivy")
        
        # Verificar el segundo contexto
        second_context = contexts[1]
        self.assertEqual(second_context["cve_id"], ["CVE-2021-67890"])
        self.assertEqual(second_context["severity"], "medium")
        self.assertEqual(second_context["component"], "another-package@2.0.0")

    def test_get_dependencies_context_from_results_empty_results(self):
        # Arrange
        empty_result = {"Results": []}
        mock_file_content = json.dumps(empty_result).encode()
        
        # Act
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('builtins.print') as mock_print:
                self.trivy_scanner.get_dependencies_context_from_results(
                    self.sample_result_path,
                    self.mock_remote_config
                )
        
        # Assert
        json_call_args = mock_print.call_args_list[1][0][0]
        parsed_json = json.loads(json_call_args)
        
        self.assertIn("dependencies_context", parsed_json)
        contexts = parsed_json["dependencies_context"]
        self.assertEqual(len(contexts), 0)

    def test_get_dependencies_context_from_results_missing_vulnerabilities(self):
        # Arrange
        result_without_vulns = {"Results": [{}]}
        mock_file_content = json.dumps(result_without_vulns).encode()
        
        # Act
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('builtins.print') as mock_print:
                self.trivy_scanner.get_dependencies_context_from_results(
                    self.sample_result_path,
                    self.mock_remote_config
                )
        
        # Assert
        json_call_args = mock_print.call_args_list[1][0][0]
        parsed_json = json.loads(json_call_args)
        
        contexts = parsed_json["dependencies_context"]
        self.assertEqual(len(contexts), 0)

    def test_get_dependencies_context_from_results_unknown_values(self):
        # Arrange
        result_with_missing_fields = {
            "Results": [
                {
                    "Vulnerabilities": [
                        {
                            # Solo algunos campos presentes para probar valores "unknown"
                            "VulnerabilityID": "CVE-2021-99999",
                            "Severity": "LOW"
                            # Faltan otros campos
                        }
                    ]
                }
            ]
        }
        mock_file_content = json.dumps(result_with_missing_fields).encode()
        
        # Act
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('builtins.print') as mock_print:
                self.trivy_scanner.get_dependencies_context_from_results(
                    self.sample_result_path,
                    self.mock_remote_config
                )
        
        # Assert
        json_call_args = mock_print.call_args_list[1][0][0]
        parsed_json = json.loads(json_call_args)
        
        contexts = parsed_json["dependencies_context"]
        self.assertEqual(len(contexts), 1)
        
        context = contexts[0]
        self.assertEqual(context["cve_id"], ["CVE-2021-99999"])
        self.assertEqual(context["severity"], "low")
        self.assertEqual(context["component"], "unknown")
        self.assertEqual(context["package_name"], "unknown")
        self.assertEqual(context["installed_version"], "unknown")
        self.assertEqual(context["fixed_version"], ["unknown"])
        self.assertEqual(context["description"], "unknown")
        self.assertEqual(context["references"], "unknown")
