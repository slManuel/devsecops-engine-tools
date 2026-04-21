import unittest
from unittest.mock import MagicMock, patch
from unittest import mock
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.aws.s3_manager import S3Manager
import datetime
import io
import json

class S3ManagerTests(unittest.TestCase):
    def setUp(self):
        self.s3_manager = S3Manager()

    @patch("boto3.session.Session.client")
    @patch("devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.aws.s3_manager.assume_role")
    def test_send_metrics(self, mock_assume_role , mock_client):
        # Mock the necessary dependencies
        mock_client.return_value = MagicMock()

        mock_assume_role.return_value.return_value = {
            "AccessKeyId": "test",
            "SecretAccessKey": "test",
            "SessionToken": "test"
        }

        # Set up test data
        config_tool = {
            "METRICS_MANAGER": {
                "AWS": {
                    "USE_ROLE": True,
                    "ROLE_ARN": "arn:aws:iam::123456789012:role/MyRole",
                    "REGION_NAME": "us-west-2",
                    "BUCKET": "my-bucket",
                    "TYPE_FORMAT_BUCKET_FILE": "json",
                    "PATH_BUCKET": "engine_tools"
                }
            }
        }
        tool = "my-tool"
        file_path = "/path/to/my/file.txt"

        with mock.patch("builtins.open", create=True) as mock_open:
            # Call the method under test
            self.s3_manager.send_metrics(config_tool, tool, file_path)

        # Assert that the necessary methods were called with the correct arguments
        mock_client.assert_called_once_with(
            service_name="s3",
            region_name="us-west-2",
            aws_access_key_id=mock.ANY,
            aws_secret_access_key=mock.ANY,
            aws_session_token=mock.ANY,
        )
        date = datetime.datetime.now()
        mock_client.return_value.put_object.assert_called_once_with(
            Bucket="my-bucket", Key=f"engine_tools/my-tool/{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}/file.json", Body=mock.ANY, ExpectedBucketOwner="123456789012"
        )

    @patch("boto3.session.Session.client")
    def test_send_metrics_without_role(self, mock_client):
        # Mock the necessary dependencies
        mock_client.return_value = MagicMock()

        # Set up test data
        config_tool = {
            "METRICS_MANAGER": {
                "AWS": {
                    "USE_ROLE": False,
                    "ROLE_ARN": "arn:aws:iam::123456789012:role/MyRole",
                    "REGION_NAME": "us-ueast-2",
                    "BUCKET": "my-bucket",
                    "TYPE_FORMAT_BUCKET_FILE": "json",
                    "PATH_BUCKET": "engine_tools"
                }
            }
        }
        tool = "my-tool"
        file_path = "/path/to/my/file.txt"

        with mock.patch("builtins.open", create=True) as mock_open:
            # Call the method under test
            self.s3_manager.send_metrics(config_tool, tool, file_path)

            # Assert that the necessary methods were called with the correct arguments
            mock_client.assert_called_once_with(
                service_name="s3",
                region_name="us-ueast-2"
            )
            date = datetime.datetime.now()
            mock_client.return_value.put_object.assert_called_once_with(
                Bucket="my-bucket", Key=f"engine_tools/my-tool/{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}/file.json", Body=mock.ANY, ExpectedBucketOwner="123456789012"
            )


    @patch("boto3.session.Session.client")
    @patch("devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.aws.s3_manager.assume_role")
    @patch("devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.aws.s3_manager.pq")
    @patch("devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.aws.s3_manager.pa")
    def test_send_metrics_parquet_with_existing_data(
        self, mock_pa, mock_pq, mock_assume_role, mock_client
    ):
        mock_client.return_value = MagicMock()
        mock_assume_role.return_value = {
            "AccessKeyId": "test",
            "SecretAccessKey": "test",
            "SessionToken": "test"
        }
        config_tool = {
            "METRICS_MANAGER": {
                "AWS": {
                    "USE_ROLE": True,
                    "ROLE_ARN": "arn:aws:iam::123456789012:role/MyRole",
                    "REGION_NAME": "us-west-2",
                    "BUCKET": "my-bucket",
                    "TYPE_FORMAT_BUCKET_FILE": "parquet",
                    "PATH_BUCKET": "engine_tools_parquet"
                }
            }
        }
        module = "my-module"
        file_path = "/tmp/test.json"
        # Mock _get_s3_data to return existing parquet data
        self.s3_manager._get_s3_data = MagicMock(return_value=b"parquetdata")
        # Mock open and json.load
        mock_json_data = {"id": "1", "date": "2024-06-01"}
        with patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_json_data))) as mock_open, \
                patch("json.load", return_value=mock_json_data):
            mock_file = MagicMock()
            mock_file.read.return_value = b"newdata"
            mock_open.return_value.__enter__.return_value = mock_file
            mock_table = MagicMock()
            mock_pq.read_table.return_value = mock_table
            mock_pa.concat_tables.return_value = mock_table
            mock_pq.write_table.return_value = None
            mock_table2 = MagicMock()
            self.s3_manager._to_arrow_record = MagicMock(return_value=mock_table2)
            buffer = io.BytesIO(b"finaldata")
            with patch("io.BytesIO", return_value=buffer):
                self.s3_manager.send_metrics(config_tool, module, file_path)
        mock_client.return_value.put_object.assert_called_once()
        args, kwargs = mock_client.return_value.put_object.call_args
        assert kwargs["Bucket"] == "my-bucket"
        assert kwargs["Key"].endswith(".parquet")
        assert isinstance(kwargs["Body"], bytes)

    @patch("boto3.session.Session.client")
    @patch("devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.aws.s3_manager.assume_role")
    def test_send_metrics_json_with_existing_data(self, mock_assume_role, mock_client):
        mock_client.return_value = MagicMock()
        mock_assume_role.return_value = {
            "AccessKeyId": "test",
            "SecretAccessKey": "test",
            "SessionToken": "test"
        }
        config_tool = {
            "METRICS_MANAGER": {
                "AWS": {
                    "USE_ROLE": True,
                    "ROLE_ARN": "arn:aws:iam::123456789012:role/MyRole",
                    "REGION_NAME": "us-west-2",
                    "BUCKET": "my-bucket",
                    "TYPE_FORMAT_BUCKET_FILE": "json",
                    "PATH_BUCKET": "engine_tools"
                }
            }
        }
        module = "my-module"
        file_path = "/tmp/test.json"
        self.s3_manager._get_s3_data = MagicMock(return_value=b"existingdata")
        with patch("builtins.open", mock.mock_open(read_data="newdata")) as mock_open:
            # Patch file read and decode
            mock_file = MagicMock()
            mock_file.read.return_value = b"newdata"
            mock_open.return_value.__enter__.return_value = mock_file
            self.s3_manager.send_metrics(config_tool, module, file_path)
        mock_client.return_value.put_object.assert_called_once()
        args, kwargs = mock_client.return_value.put_object.call_args
        assert kwargs["Bucket"] == "my-bucket"
        assert kwargs["Key"].endswith(".json")
        assert "existingdata" in kwargs["Body"]
        assert "newdata" in kwargs["Body"]

    @patch("boto3.session.Session.client")
    @patch("devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.aws.s3_manager.assume_role")
    def test_send_metrics_unsupported_format(self, mock_assume_role, mock_client):
        mock_client.return_value = MagicMock()
        mock_assume_role.return_value = {
            "AccessKeyId": "test",
            "SecretAccessKey": "test",
            "SessionToken": "test"
        }
        config_tool = {
            "METRICS_MANAGER": {
                "AWS": {
                    "USE_ROLE": True,
                    "ROLE_ARN": "arn:aws:iam::123456789012:role/MyRole",
                    "REGION_NAME": "us-west-2",
                    "BUCKET": "my-bucket",
                    "TYPE_FORMAT_BUCKET_FILE": "csv",
                    "PATH_BUCKET": "engine_tools"
                }
            }
        }
        module = "my-module"
        file_path = "/tmp/test.csv"
        self.s3_manager._get_s3_data = MagicMock(return_value=b'irrelevant')
        with patch("builtins.open", mock.mock_open(read_data="irrelevant")) as mock_open:
            with self.assertRaises(ValueError):
                # Patch file read and decode
                mock_file = MagicMock()
                mock_file.read.return_value = b"newdata"
                mock_open.return_value.__enter__.return_value = mock_file
                self.s3_manager.send_metrics(config_tool, module, file_path)
