import io
import os
import re
import json
import stat
import glob
import base64
import shutil
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan import (  # noqa: E501
    PrismaCloudManagerScan,
)


class TestPrismaCloudManagerScan(unittest.TestCase):
    def setUp(self):
        # Carpeta temporal para archivos de prueba
        self.tmpdir = tempfile.mkdtemp(prefix="unittest_prisma_")
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir, ignore_errors=True))

        # Config remota simulada
        self.remoteconfig = {
            "PRISMA_CLOUD": {
                "PRISMA_CONSOLE_URL": "https://console.example",
                "PRISMA_ACCESS_KEY": "AK_xxx",
                "PRISMA_API_VERSION": "v1",
                "TWISTCLI_PATH": "twistcli.exe",  # ruta relativa que se antepone con os.getcwd()
            }
        }

        # dict_args básico
        self.dict_args = {"folder_path": self.tmpdir}

        # Instancia bajo prueba (tool_run no se usa dentro de los métodos, podemos pasar un stub)
        self.sut = PrismaCloudManagerScan(tool_run=SimpleNamespace(), dict_args=self.dict_args)

    # ----------------------------
    # download_twistcli
    # ----------------------------

    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.os.chmod")  # noqa: E501
    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.requests.get")  # noqa: E501
    def test_download_twistcli_success(self, mock_get, mock_chmod):
        file_path = os.path.join(self.tmpdir, "twistcli.exe")

        # Simula respuesta OK
        resp = MagicMock()
        resp.content = b"FAKE_BINARY"
        resp.raise_for_status.return_value = None
        mock_get.return_value = resp

        ret = self.sut.download_twistcli(
            file_path=file_path,
            prisma_access_key="AK",
            prisma_secret_key="SK",
            prisma_console_url="https://console.prisma",
            prisma_api_version="v1",
        )
        self.assertEqual(ret, 0)
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "rb") as f:
            self.assertEqual(f.read(), b"FAKE_BINARY")

        # Verifica encabezado Basic calculado
        called_headers = mock_get.call_args.kwargs.get("headers") or {}
        self.assertIn("Authorization", called_headers)
        b64 = base64.b64encode(b"AK:SK").decode()
        self.assertEqual(called_headers["Authorization"], f"Basic {b64}")
        mock_chmod.assert_called_once()
        resp.raise_for_status.assert_called_once()

    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.requests.get")  # noqa: E501
    def test_download_twistcli_failure(self, mock_get):
        file_path = os.path.join(self.tmpdir, "twistcli.exe")

        # Simula HTTP error
        resp = MagicMock()
        def _raise():
            from requests import HTTPError
            raise HTTPError("boom")
        resp.raise_for_status.side_effect = _raise
        mock_get.return_value = resp

        with self.assertRaises(ValueError) as cm:
            self.sut.download_twistcli(
                file_path=file_path,
                prisma_access_key="AK",
                prisma_secret_key="SK",
                prisma_console_url="https://console.prisma",
                prisma_api_version="v1",
            )
        self.assertRegex(str(cm.exception), r"Error downloading twistcli:")

    # ----------------------------
    # scan_function
    # ----------------------------

    @patch("builtins.print")
    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.glob.glob")  # noqa: E501
    def test_scan_function_no_zip_returns_none(self, mock_glob, mock_print):
        mock_glob.return_value = []
        ret = self.sut.scan_function(
            file_path=os.path.join(self.tmpdir, "twistcli"),
            folder_path=self.tmpdir,
            remoteconfig=self.remoteconfig,
            prisma_secret_key="SK",
        )
        self.assertIsNone(ret)
        # Mensaje de advertencia (no necesariamente validamos contenido exacto)
        mock_print.assert_called()

    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.subprocess.run")  # noqa: E501
    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.glob.glob")  # noqa: E501
    def test_scan_function_success(self, mock_glob, mock_run):
        # Crea un ZIP ficticio en la carpeta
        fake_zip = os.path.join(self.tmpdir, "myfun.zip")
        with open(fake_zip, "wb") as f:
            f.write(b"ZIPDATA")
        mock_glob.return_value = [fake_zip]

        # Salida simulada de twistcli
        stdout = (
            "Scan results for: function myfun.zip\n"
            "Compliance found for function myfun.zip: total - 2, critical - 1, high - 0, medium - 1, low - 0\n"
            "Vulnerabilities found for function myfun.zip: total - 1, critical - 0, high - 1, medium - 0, low - 0\n"
            "| CVE-2025-0001 | High | 8.8 | pkgA | 1.2.3 | Open | 2025-01-02 | 2025-01-03 | terrible bug |\n"
            "Compliance threshold check results: PASS\n"
            "Vulnerability threshold check results: PASS\n"
        )
        cp = SimpleNamespace(stdout=stdout, stderr="", returncode=0)
        mock_run.return_value = cp

        result = self.sut.scan_function(
            file_path=os.path.join(self.tmpdir, "twistcli"),
            folder_path=self.tmpdir,
            remoteconfig=self.remoteconfig,
            prisma_secret_key="SK",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertEqual(result["results"][0]["name"], "myfun.zip")
        self.assertEqual(result["results"][0]["complianceDistribution"]["total"], 2)
        self.assertTrue(result["results"][0]["complianceScanPassed"])
        self.assertEqual(result["results"][0]["vulnerabilityDistribution"]["total"], 1)
        self.assertTrue(result["results"][0]["vulnerabilityScanPassed"])
        self.assertEqual(result["results"][0]["vulnerabilities"][0]["id"], "CVE-2025-0001")

    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.subprocess.run")  # noqa: E501
    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.glob.glob")  # noqa: E501
    def test_scan_function_calledprocesserror_returns_none(self, mock_glob, mock_run):
        # Hay un zip, pero el comando falla
        fake_zip = os.path.join(self.tmpdir, "thefun.zip")
        with open(fake_zip, "wb") as f:
            f.write(b"ZIPDATA")
        mock_glob.return_value = [fake_zip]

        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(returncode=1, cmd=["twistcli"])

        ret = self.sut.scan_function(
            file_path=os.path.join(self.tmpdir, "twistcli"),
            folder_path=self.tmpdir,
            remoteconfig=self.remoteconfig,
            prisma_secret_key="SK",
        )
        self.assertIsNone(ret)

    # ----------------------------
    # parse_scan_results
    # ----------------------------

    def test_parse_scan_results_full(self):
        stdout = (
            "Scan results for: function fn.zip\n"
            "Compliance found for function fn.zip: total - 3, critical - 1, high - 1, medium - 1, low - 0\n"
            "Vulnerabilities found for function fn.zip: total - 2, critical - 1, high - 0, medium - 1, low - 0\n"
            "| CVE-123 | Critical | 9.9 | libX | 2.0 | Open | 2025-01-01 | 2025-02-01 | desc critical |\n"
            "| CVE-456 | Medium | 5.0 | libY | 1.0 | Fixed | 2025-01-10 | 2025-02-02 | desc medium |\n"
            "Compliance threshold check results: PASS\n"
            "Vulnerability threshold check results: PASS\n"
        )
        data = self.sut.parse_scan_results(stdout)
        self.assertEqual(data["results"][0]["name"], "fn.zip")
        self.assertEqual(data["results"][0]["complianceDistribution"]["critical"], 1)
        self.assertEqual(len(data["results"][0]["vulnerabilities"]), 2)
        self.assertTrue(data["results"][0]["vulnerabilityScanPassed"])

    def test_parse_scan_results_minimal(self):
        # Sin líneas de distribución ni tabla; debe producir valores por defecto razonables
        stdout = "Scan results for: function something.zip\n"
        data = self.sut.parse_scan_results(stdout)
        self.assertEqual(data["results"][0]["name"], "something.zip")
        self.assertEqual(data["results"][0]["complianceDistribution"], {})
        self.assertEqual(data["results"][0]["vulnerabilityDistribution"], {})
        self.assertFalse(data["results"][0]["complianceScanPassed"])
        self.assertFalse(data["results"][0]["vulnerabilityScanPassed"])
        self.assertEqual(data["results"][0]["vulnerabilities"], [])

    # ----------------------------
    # run_tool_function_sca
    # ----------------------------

    @patch("builtins.print")
    def test_run_tool_function_sca_skip_true_returns_0(self, mock_print):
        ret = self.sut.run_tool_function_sca(
            remoteconfig=self.remoteconfig,
            prisma_secret_key="SK",
            skip_flag=True,
        )
        self.assertEqual(ret, 0)
        mock_print.assert_called()

    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.os.path.exists")  # noqa: E501
    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.os.getcwd")  # noqa: E501
    def test_run_tool_function_sca_downloads_if_missing_and_scans(self, mock_getcwd, mock_exists):
        # Simula CWD (para que construya correctamente el path del twistcli)
        mock_getcwd.return_value = self.tmpdir
        # No existe el twistcli → debe descargar
        mock_exists.return_value = False

        # Mock de download_twistcli (debe ser llamado)
        with patch.object(self.sut, "download_twistcli", return_value=0) as m_dl, \
             patch.object(self.sut, "scan_function", return_value={"ok": True}) as m_scan:

            ret = self.sut.run_tool_function_sca(
                remoteconfig=self.remoteconfig,
                prisma_secret_key="SK",
                skip_flag=False,
            )
            self.assertEqual(ret, {"ok": True})
            m_dl.assert_called_once()
            # Verifica que scan_function haya sido llamado con el path completo
            expected_twistcli_path = os.path.join(self.tmpdir, self.remoteconfig["PRISMA_CLOUD"]["TWISTCLI_PATH"])
            args, kwargs = m_scan.call_args
            self.assertEqual(args[0], expected_twistcli_path)  # file_path

    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.os.path.exists")  # noqa: E501
    @patch("devsecops_engine_tools.engine_sca.engine_function.src.infrastructure.driven_adapters.prisma_cloud.prisma_cloud_manager_scan.os.getcwd")  # noqa: E501
    def test_run_tool_function_sca_scan_raises_returns_none(self, mock_getcwd, mock_exists):
        mock_getcwd.return_value = self.tmpdir
        mock_exists.return_value = True  # ya existe twistcli, no descarga

        with patch.object(self.sut, "scan_function", side_effect=RuntimeError("boom")) as m_scan:
            ret = self.sut.run_tool_function_sca(
                remoteconfig=self.remoteconfig,
                prisma_secret_key="SK",
                skip_flag=False,
            )
            self.assertIsNone(ret)
            m_scan.assert_called_once()


if __name__ == "__main__":
    unittest.main()
