from devsecops_engine_tools.engine_core.src.domain.model.gateway.metrics_manager_gateway import (
    MetricsManagerGateway,
)
from devsecops_engine_tools.engine_core.src.infrastructure.helpers.aws import (
    assume_role,
)
import boto3
import logging
import datetime
import io
import pyarrow as pa
import pyarrow.parquet as pq
import json

boto3.set_stream_logger(name="botocore.credentials", level=logging.WARNING)


class S3Manager(MetricsManagerGateway):

    # ---- Events ----
    event_schema = pa.struct(
        [
            ("timestamp", pa.string()),
            ("level", pa.string()),
            ("message", pa.string()),
            ("module", pa.string()),
            ("funcName", pa.string()),
            ("lineno", pa.int64()),
        ]
    )

    # ---- Findings Excluded ----
    finding_excluded_schema = pa.struct(
        [
            ("id", pa.string()),
            ("severity", pa.string()),
            ("priority", pa.string()),
            ("category", pa.string()),
        ]
    )

    # ---- Vulnerabilities ----
    vuln_threshold_schema = pa.struct(
        [
            ("very_critical", pa.int64()),
            ("critical", pa.int64()),
            ("high", pa.int64()),
            ("medium", pa.int64()),
            ("low", pa.int64()),
            ("medium_low", pa.int64()),
        ]
    )

    vuln_found_schema = pa.struct(
        [
            ("id", pa.string()),
            ("severity", pa.string()),
            ("priority", pa.string()),
        ]
    )

    vulnerabilities_schema = pa.struct(
        [
            ("model_break_build", pa.string()),
            ("threshold", vuln_threshold_schema),
            ("status", pa.string()),
            ("found", pa.list_(vuln_found_schema)),
        ]
    )

    # ---- Compliances ----
    compliances_schema = pa.struct(
        [
            ("threshold", pa.struct([("critical", pa.int64())])),
            ("status", pa.string()),
            ("found", pa.list_(vuln_found_schema)),
        ]
    )

    # ---- Risk ----
    risk_control_schema = pa.struct(
        [
            ("remediation_rate", pa.float64()),
            ("blacklisted", pa.int64()),
            ("max_risk_score", pa.float64()),
        ]
    )

    risk_found_schema = pa.struct(
        [
            ("id", pa.string()),
            ("severity", pa.string()),
            ("risk_score", pa.string()),
            ("reason", pa.string()),
        ]
    )

    risk_schema = pa.struct(
        [
            ("risk_control", risk_control_schema),
            ("status", pa.string()),
            ("found", pa.list_(risk_found_schema)),
        ]
    )

    # ---- Scan Result ----
    scan_result_schema = pa.struct(
        [
            ("findings_excluded", pa.list_(finding_excluded_schema)),
            ("vulnerabilities", vulnerabilities_schema),
            ("compliances", compliances_schema),
            ("risk", risk_schema),
        ]
    )

    record_schema = pa.schema(
        [
            ("id", pa.string()),
            ("date", pa.string()),
            ("component", pa.string()),
            ("stage", pa.string()),
            ("check_type", pa.string()),
            ("environment", pa.string()),
            ("events", pa.list_(event_schema)),
            ("scan_result", scan_result_schema),
        ]
    )

    def send_metrics(self, config_tool, module, file_path):
        credentials_role = (
            assume_role(config_tool["METRICS_MANAGER"]["AWS"]["ROLE_ARN"])
            if config_tool["METRICS_MANAGER"]["AWS"]["USE_ROLE"]
            else None
        )
        session = boto3.session.Session()

        if credentials_role:
            client = session.client(
                service_name="s3",
                region_name=config_tool["METRICS_MANAGER"]["AWS"]["REGION_NAME"],
                aws_access_key_id=credentials_role["AccessKeyId"],
                aws_secret_access_key=credentials_role["SecretAccessKey"],
                aws_session_token=credentials_role["SessionToken"],
            )
        else:
            client = session.client(
                service_name="s3",
                region_name=config_tool["METRICS_MANAGER"]["AWS"]["REGION_NAME"],
            )
        date = datetime.datetime.now()
        type_format = config_tool["METRICS_MANAGER"]["AWS"]["TYPE_FORMAT_BUCKET_FILE"]
        path_bucket_metrics = config_tool["METRICS_MANAGER"]["AWS"]["PATH_BUCKET"]
        filename = file_path.split("/")[-1]
        base_path = f"{path_bucket_metrics}/module={module}/year={date:%Y}/month={date:%m}" if type_format == "parquet" else f"{path_bucket_metrics}/{module}/{date:%Y}/{date:%m}/{date:%d}"
        path_bucket = f"{base_path}/{filename.rsplit('.', 1)[0]}.{type_format}"

        existing_data = self._get_s3_data(
            client, config_tool["METRICS_MANAGER"]["AWS"]["BUCKET"], path_bucket
        )

        if (
            type_format
            == "parquet"
        ):
            buffer = io.BytesIO()
            with open(file_path, "rb") as new_data:
                new_json_data = json.load(new_data)

            new_table = self._to_arrow_record(new_json_data)

            if existing_data:
                existing_table = pq.read_table(
                    io.BytesIO(existing_data), schema=self.record_schema
                )
                final_table = pa.concat_tables([existing_table, new_table])
            else:
                final_table = new_table

            pq.write_table(
                final_table,
                buffer,
                compression="snappy",
                use_deprecated_int96_timestamps=False,
            )
            buffer.seek(0)
            data = buffer.getvalue()
        elif type_format == "json":
            with open(file_path, "rb") as new_data:
                new_data_content = new_data.read().decode("utf-8")
                data = (
                    existing_data.decode("utf-8") + "\n" + new_data_content
                    if existing_data
                    else new_data_content
                )
        else:
            raise ValueError(
                "Unsupported TYPE_FORMAT_BUCKET_FILE. Use 'parquet' or 'json'."
            )

        client.put_object(
            Bucket=config_tool["METRICS_MANAGER"]["AWS"]["BUCKET"],
            Key=path_bucket,
            Body=data,
        )

    def _get_s3_data(self, client, bucket, path):
        try:
            response = client.get_object(
                Bucket=bucket,
                Key=path,
            )
            return response["Body"].read()
        except client.exceptions.NoSuchKey:
            return ""

    def _to_arrow_record(self, event: dict) -> pa.Table:
        event = dict(event)

        data = {
            "id": [event.get("id")],
            "date": [event.get("date")],  # "YYYY-MM-DD"
            "component": [event.get("component")],
            "stage": [event.get("stage")],
            "check_type": [event.get("check_type")],
            "environment": [event.get("environment")],
            "events": [event.get("events", [])],
            "scan_result": [
                event.get(
                    "scan_result",
                    {
                        "findings_excluded": [],
                        "vulnerabilities": None,
                        "compliances": None,
                        "risk": None,
                    },
                )
            ],
        }

        return pa.Table.from_pydict(data, schema=self.record_schema)
