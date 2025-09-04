import pytest
from unittest.mock import patch, MagicMock, Mock
from devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils import TrivyManagerScanUtils


@pytest.fixture
def trivy_utils_instance():
    return TrivyManagerScanUtils()


def test_download_tool_success(trivy_utils_instance):
    """Test download_tool method in TrivyManagerScanUtils"""
    with patch("builtins.open") as mock_open, patch(
        "requests.get"
        ) as mock_request:

        trivy_utils_instance._download_tool("file", "url")

        assert mock_request.call_count == 1
        assert mock_open.call_count == 1


def test_download_tool_exception(trivy_utils_instance):
    """Test download_tool exception handling in TrivyManagerScanUtils"""
    with patch("requests.get") as mock_request, patch(
            "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.logger.error"
        ) as mock_logger:
        mock_request.side_effect = Exception("custom error")

        trivy_utils_instance._download_tool("file", "url")

        mock_logger.assert_called_with("Error downloading trivy: custom error")


def test_install_tool_success(trivy_utils_instance):
    """Test _install_tool method in TrivyManagerScanUtils"""
    with patch("subprocess.run") as mock_run, patch(
        "tarfile.open"
    ) as mock_tar_open, patch(
        "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils._download_tool"
    ) as mock_download:
        mock_run.return_value = Mock(returncode=1)

        trivy_utils_instance._install_tool("file", "url", "trivy")

        assert mock_tar_open.call_count == 1


def test_install_tool_exception(trivy_utils_instance):
    """Test _install_tool exception handling in TrivyManagerScanUtils"""
    with patch("subprocess.run") as mock_run, patch(
        "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.logger.error"
        ) as mock_logger, patch(
        "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils._download_tool"
        ) as mock_download:
        mock_run.return_value = Mock(returncode=1)
        mock_download.side_effect = Exception("custom error")

        trivy_utils_instance._install_tool("file", "url", "trivy")

        mock_logger.assert_called_with("Error installing trivy: custom error")


def test_install_tool_windows_success(trivy_utils_instance):
    """Test _install_tool_windows method in TrivyManagerScanUtils"""
    with patch("subprocess.run") as mock_run, patch(
        "zipfile.ZipFile"
    ) as mock_zipfile, patch(
        "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils._download_tool"
    ) as mock_download:
        mock_run.side_effect = Exception()

        trivy_utils_instance._install_tool_windows("file", "url", "trivy.exe")

        assert mock_zipfile.call_count == 1


def test_install_tool_windows_exception(trivy_utils_instance):
    """Test _install_tool_windows exception handling in TrivyManagerScanUtils"""
    with patch("subprocess.run") as mock_run, patch(
        "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.logger.error"
        ) as mock_logger, patch(
        "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils._download_tool"
        ) as mock_download:
        mock_run.side_effect = Exception()
        mock_download.side_effect = Exception("custom error")

        trivy_utils_instance._install_tool_windows("file", "url", "trivy.exe")

        mock_logger.assert_called_with("Error installing trivy: custom error")


def test_identify_os_and_install_linux(trivy_utils_instance):
    """Test identify_os_and_install for Linux platform"""
    with patch("platform.system") as mock_platform, patch("platform.architecture") as mock_arch, patch(
        "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils._install_tool"
    ) as mock_install:
        mock_platform.return_value = "Linux"
        mock_arch.return_value = ("64bit", "")
        mock_install.return_value = "./trivy"
        version = "1.2.3"
        
        result = trivy_utils_instance.identify_os_and_install(version)
        
        expected_file = f"trivy_{version}_Linux-64bit.tar.gz"
        expected_url = f"https://github.com/aquasecurity/trivy/releases/download/v{version}/{expected_file}"
        mock_install.assert_called_with(expected_file, expected_url, "trivy")
        assert result == "./trivy"


def test_identify_os_and_install_darwin(trivy_utils_instance):
    """Test identify_os_and_install for macOS platform"""
    with patch("platform.system") as mock_platform, patch("platform.architecture") as mock_arch, patch(
        "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils._install_tool"
    ) as mock_install:
        mock_platform.return_value = "Darwin"
        mock_arch.return_value = ("64bit", "")
        mock_install.return_value = "./trivy"
        version = "1.2.3"
        
        result = trivy_utils_instance.identify_os_and_install(version)
        
        expected_file = f"trivy_{version}_macOS-64bit.tar.gz"
        expected_url = f"https://github.com/aquasecurity/trivy/releases/download/v{version}/{expected_file}"
        mock_install.assert_called_with(expected_file, expected_url, "trivy")
        assert result == "./trivy"


def test_identify_os_and_install_windows(trivy_utils_instance):
    """Test identify_os_and_install for Windows platform"""
    with patch("platform.system") as mock_platform, patch("platform.architecture") as mock_arch, patch(
        "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.TrivyManagerScanUtils._install_tool_windows"
    ) as mock_install:
        mock_platform.return_value = "Windows"
        mock_arch.return_value = ("64bit", "")
        mock_install.return_value = "./trivy.exe"
        version = "1.2.3"
        
        result = trivy_utils_instance.identify_os_and_install(version)
        
        expected_file = f"trivy_{version}_windows-64bit.zip"
        expected_url = f"https://github.com/aquasecurity/trivy/releases/download/v{version}/{expected_file}"
        mock_install.assert_called_with(expected_file, expected_url, "trivy.exe")
        assert result == "./trivy.exe"


def test_identify_os_and_install_unsupported(trivy_utils_instance):
    """Test identify_os_and_install for unsupported platform"""
    with patch("platform.system") as mock_platform, patch(
        "devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils.logger.warning"
    ) as mock_logger:
        mock_platform.return_value = "UnsupportedOS"
        version = "1.2.3"
        
        result = trivy_utils_instance.identify_os_and_install(version)
        
        mock_logger.assert_called_with("UnsupportedOS is not supported.")
        assert result is None
