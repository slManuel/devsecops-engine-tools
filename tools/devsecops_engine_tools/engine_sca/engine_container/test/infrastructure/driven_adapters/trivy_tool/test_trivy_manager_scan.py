from devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan import (
    TrivyScan,
)
from devsecops_engine_tools.engine_core.src.domain.model.component import Component

from unittest.mock import patch, MagicMock, Mock
import pytest
import subprocess


@pytest.fixture
def trivy_scan_instance():
    return TrivyScan()


def test_scan_image_success(trivy_scan_instance):
    with patch("subprocess.run") as mock_run, patch(
        "builtins.print"
    ) as mock_print:
        result = trivy_scan_instance.scan_image("prefix", "image_name", "result.json","base_image", "os,library")

        assert mock_print.call_count == 1
        assert result == 'result.json'


def test_scan_image_exception(trivy_scan_instance):
    with patch("subprocess.run") as mock_run, patch(
        "devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.logger.error"
        ) as mock_logger:
        mock_run.side_effect = Exception("custom error")

        trivy_scan_instance.scan_image("prefix", "image_name", "result.json","base_image", "os,library")

        mock_logger.assert_called_with("Unexpected error during image scan of image_name: custom error")


def test_run_tool_container_sca_success(trivy_scan_instance):
    with patch("devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils.identify_os_and_install") as mock_identify:
        remote_config = {"TRIVY":{"TRIVY_VERSION": "1.2.3"}}
        mock_identify.return_value = "trivy"
        trivy_scan_instance.scan_image = MagicMock()
        trivy_scan_instance.scan_image.return_value = "result.json"
        version = remote_config["TRIVY"]["TRIVY_VERSION"]

        result = trivy_scan_instance.run_tool_container_sca(remote_config, None, None, "image_name", "result.json", "base_image", "exclusions", False, None)

        mock_identify.assert_called_with(version)
        assert result == ("result.json", None)


def test_run_tool_container_sca_with_sbom(trivy_scan_instance):
    with patch("devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils.identify_os_and_install") as mock_identify:
        remote_config = {"TRIVY":{"TRIVY_VERSION": "1.2.3"}}
        mock_identify.return_value = "trivy"
        trivy_scan_instance.scan_image = MagicMock()
        trivy_scan_instance.scan_image.return_value = "result.json"
        trivy_scan_instance._generate_sbom = MagicMock()
        trivy_scan_instance._generate_sbom.return_value = [Component("component1", "version1")]
        version = remote_config["TRIVY"]["TRIVY_VERSION"]

        result = trivy_scan_instance.run_tool_container_sca(remote_config, None, None, "image_name", "result.json", "base_image","exclusions", True, None)

        mock_identify.assert_called_with(version)
        assert result == ("result.json", [Component("component1", "version1")])


def test_run_tool_container_sca_none(trivy_scan_instance):
    with patch("devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils.identify_os_and_install") as mock_identify:
        remote_config = {"TRIVY":{"TRIVY_VERSION": "1.2.3"}}
        mock_identify.return_value = None

        result = trivy_scan_instance.run_tool_container_sca(remote_config, None, None, "image_name", "result.json", "base_image","exclusions", False, None)

        assert result == None


@patch('devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.subprocess.run')
@patch('devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.get_list_component')
def test_generate_sbom_success(mock_get_list_component, mock_subprocess_run):
    # Configurar los mocks
    mock_subprocess_run.return_value = MagicMock()
    mock_get_list_component.return_value = ["component1", "component2"]

    # Crear instancia de TrivyScan
    trivy_scan = TrivyScan()

    # Datos de prueba
    prefix = "trivy"
    image_name = "test_image"
    remoteconfig = {
        "TRIVY": {
            "SBOM_FORMAT": "json"
        }
    }
    vuln_type = "os,library"

    # Llamar a la función
    result = trivy_scan._generate_sbom(prefix, image_name, remoteconfig, vuln_type)

    # Verificar que se llamaron las funciones esperadas
    mock_subprocess_run.assert_called_once_with(
        [
            prefix,
            "image",
            "--format",
            "json",
            "--output",
            f"{image_name.replace('/', '_')}_SBOM.json",
            "--pkg-types",
            vuln_type,
            "--quiet",
            image_name,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    mock_get_list_component.assert_called_once_with(f"{image_name.replace('/', '_')}_SBOM.json", "json")
    assert result, ["component1", "component2"]


@patch('devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.subprocess.run')
@patch('devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.logger')
def test_generate_sbom_failure(mock_logger, mock_subprocess_run):
    # Configurar los mocks
    mock_subprocess_run.side_effect = Exception("Test exception")

    # Crear instancia de TrivyScan
    trivy_scan = TrivyScan()

    # Datos de prueba
    prefix = "trivy"
    image_name = "test_image"
    remoteconfig = {
        "TRIVY": {
            "SBOM_FORMAT": "json"
        }
    }
    vuln_type = "os,library"

    # Llamar a la función y verificar que se lanza la excepción esperada
    trivy_scan._generate_sbom(prefix, image_name, remoteconfig, vuln_type)

    mock_logger.error.assert_called_once_with("Unexpected error generating SBOM: Test exception")


@patch('devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.subprocess.run')
def test_scan_image_compressed_file(mock_subprocess_run):
    """Test scanning a compressed file"""
    mock_subprocess_run.return_value = None

    trivy_scan = TrivyScan()
    prefix = "trivy"
    image_name = "/path/to/image.tar.gz"
    result_file = "result.json"
    base_image = None
    vuln_type = "os,library"

    result = trivy_scan.scan_image(prefix, image_name, result_file, base_image, vuln_type, is_compressed_file=True)

    assert result == result_file
    mock_subprocess_run.assert_called_once_with(
        [
            prefix,
            "--scanners",
            "vuln",
            "-f",
            "json",
            "-o",
            result_file,
            "--pkg-types",
            vuln_type,
            "--quiet",
            "image",
            "--input",
            image_name,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


@patch('devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.subprocess.run')
def test_scan_image_regular_image(mock_subprocess_run):
    """Test scanning a regular Docker image"""
    mock_subprocess_run.return_value = None

    trivy_scan = TrivyScan()
    prefix = "trivy"
    image_name = "nginx:latest"
    result_file = "result.json"
    base_image = None
    vuln_type = "os,library"

    result = trivy_scan.scan_image(prefix, image_name, result_file, base_image, vuln_type, is_compressed_file=False)

    assert result == result_file
    mock_subprocess_run.assert_called_once_with(
        [
            prefix,
            "--scanners",
            "vuln",
            "-f",
            "json",
            "-o",
            result_file,
            "--pkg-types",
            vuln_type,
            "--quiet",
            "image",
            image_name,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


@patch('devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.get_list_component')
@patch('devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.subprocess.run')
def test_generate_sbom_compressed_file(mock_subprocess_run, mock_get_list_component):
    """Test SBOM generation for compressed file"""
    mock_subprocess_run.return_value = None
    mock_get_list_component.return_value = ["component1", "component2"]

    trivy_scan = TrivyScan()
    prefix = "trivy"
    image_name = "/path/to/image.tar.gz"
    remoteconfig = {
        "TRIVY": {
            "SBOM_FORMAT": "json"
        }
    }
    vuln_type = "os,library"

    result = trivy_scan._generate_sbom(prefix, image_name, remoteconfig, vuln_type, is_compressed_file=True)

    mock_subprocess_run.assert_called_once_with(
        [
            prefix,
            "image",
            "--format",
            "json",
            "--output",
            f"{image_name.replace('/', '_')}_SBOM.json",
            "--pkg-types",
            "os,library",
            "--quiet",
            "--input",
            image_name,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    mock_get_list_component.assert_called_once_with(f"{image_name.replace('/', '_')}_SBOM.json", "json")
    assert result, ["component1", "component2"]


@patch('devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.TrivyScan.scan_image')
@patch('devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_manager_scan.TrivyScan._generate_sbom')
@patch('devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils.identify_os_and_install')
def test_run_tool_container_sca_compressed_file(mock_identify_os, mock_generate_sbom, mock_scan_image):
    """Test running SCA tool with compressed file"""
    mock_identify_os.return_value = "trivy"
    mock_scan_image.return_value = "result.json"
    mock_generate_sbom.return_value = ["component1"]

    trivy_scan = TrivyScan()
    remoteconfig = {
        "TRIVY": {
            "TRIVY_VERSION": "0.48.1",
            "SBOM_FORMAT": "json"
        }
    }

    result = trivy_scan.run_tool_container_sca(
        remoteconfig=remoteconfig,
        secret_tool=None,
        token_engine_container=None,
        image_name="/path/to/image.tar.gz",
        result_file="result.json",
        base_image=None,
        exclusions={},
        generate_sbom=True,
        docker_address=None,
        is_compressed_file=True
    )

    mock_identify_os.assert_called_once_with("0.48.1")
    mock_scan_image.assert_called_once_with(
        "trivy", "/path/to/image.tar.gz", "result.json", None, "os,library", False, True
    )
    mock_generate_sbom.assert_called_once_with(
        "trivy", "/path/to/image.tar.gz", remoteconfig, "os,library", False, True
    )
    assert result == ("result.json", ["component1"])
