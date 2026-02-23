import base64
import json
import os
import unittest
from unittest.mock import mock_open, patch

from devsecops_engine_tools.engine_utilities.sbom.sbom_file_reader import (
    read_sbom_file_as_base64,
)


class TestReadSbomFileAsBase64(unittest.TestCase):

    def test_success_returns_base64_string(self):
        """Covers lines 6-8, 11-16: file exists, valid JSON, returns base64."""
        sbom_filename = "my_SBOM.json"
        content = '{"components": []}'
        expected_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        expected_path = os.path.join("/fake/cwd", sbom_filename)

        with patch("devsecops_engine_tools.engine_utilities.sbom.sbom_file_reader.os.getcwd", return_value="/fake/cwd"), \
             patch("devsecops_engine_tools.engine_utilities.sbom.sbom_file_reader.os.path.isfile", return_value=True), \
             patch("builtins.open", mock_open(read_data=content)):
            result = read_sbom_file_as_base64(sbom_filename)

        self.assertEqual(result, expected_b64)

    def test_file_not_found_raises(self):
        """Covers line 9: FileNotFoundError raised when file does not exist."""
        sbom_filename = "missing_SBOM.json"
        fake_path = os.path.join("/fake/cwd", sbom_filename)

        with patch("devsecops_engine_tools.engine_utilities.sbom.sbom_file_reader.os.getcwd", return_value="/fake/cwd"), \
             patch("devsecops_engine_tools.engine_utilities.sbom.sbom_file_reader.os.path.isfile", return_value=False):
            with self.assertRaises(FileNotFoundError) as ctx:
                read_sbom_file_as_base64(sbom_filename)

        self.assertIn("SBOM file not found", str(ctx.exception))
        self.assertIn(fake_path, str(ctx.exception))

    def test_invalid_json_raises(self):
        """Covers line 14: json.loads raises on invalid JSON content."""
        sbom_filename = "bad_SBOM.json"
        invalid_content = "not valid json {"

        with patch("devsecops_engine_tools.engine_utilities.sbom.sbom_file_reader.os.getcwd", return_value="/fake/cwd"), \
             patch("devsecops_engine_tools.engine_utilities.sbom.sbom_file_reader.os.path.isfile", return_value=True), \
             patch("builtins.open", mock_open(read_data=invalid_content)):
            with self.assertRaises(json.JSONDecodeError):
                read_sbom_file_as_base64(sbom_filename)


if __name__ == "__main__":
    unittest.main()
