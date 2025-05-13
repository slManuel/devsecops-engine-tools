import { OutputChannel } from "vscode";
import OutputManager from "../helper/OutputManager";
import { exec } from "child_process";

import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import { Finding } from "../../domain/model/Finding";
import { ScannerRes } from "../../domain/model/ScannerRes";

export class ImageScanner implements IScannerGateway {
  scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    dockerImageName: string,
    toolVersion: string
  ): Promise<ScannerRes> {
    let scanResult: boolean = false;
    let findings: Finding[] = [];
    exec(
      `/usr/local/bin/docker run --rm -v /var/run/docker.sock:/var/run/docker.sock ${dockerImageName}:${toolVersion} devsecops-engine-tools --platform_devops local --remote_config_repo docker_default_remote_config --module engine_container --tool trivy --image_to_scan ${elementToScan}`,
      (error, stdout, stderr) => {
        if (error) {
          console.error(`exec error: ${error}`);
          console.error(`stderr: ${stderr}`);
        }

        const cleanedOutput = OutputManager.removeAnsiEscapeCodes(stdout);
        outputChannel.appendLine("IMAGE SCAN OUTPUT:");
        outputChannel.appendLine(cleanedOutput);
        outputChannel.show();
        scanResult = true;
        const scanDataResult = JSON.parse(iacScannerDummyContext);
        findings = scanDataResult.iac_context.map((finding: Finding) => {
          return new Finding(
            finding.getId(),
            finding.getCustomVulnId(),
            finding.getCheckName(),
            finding.getCheckClass(),
            finding.getSeverity(),
            finding.getWhere(),
            finding.getResource(),
            finding.getDescription(),
            finding.getModule(),
            finding.getTool()
          );
        });
      }
    );
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(new ScannerRes(scanResult, findings));
      }, 1000000);
    });
  }
}

const iacScannerDummyContext = `
{
    "iac_context": [
        {
            "id": "CKV_AWS_54",
            "custom_vuln_id": "CKV_AWS_54",
            "check_name": "Ensure S3 bucket has block public policy enabled",
            "check_class": "checkov.cloudformation.checks.resource.aws.S3BlockPublicPolicy",
            "severity": "medium",
            "where": "/ms_artifact/cloudformation_test.template.yaml: AWS::S3::Bucket.UnsecureS3Bucket (line 5-15)",
            "resource": "AWS::S3::Bucket.UnsecureS3Bucket",
            "description": "Ensure S3 bucket has block public policy enabled",
            "module": "engine_iac",
            "tool": "Checkov"
        },
        {
            "id": "CKV_AWS_53",
            "custom_vuln_id": "CKV_AWS_53",
            "check_name": "Ensure S3 bucket has block public ACLS enabled",
            "check_class": "checkov.cloudformation.checks.resource.aws.S3BlockPublicACLs",
            "severity": "high",
            "where": "/ms_artifact/cloudformation_test.template.yaml: AWS::S3::Bucket.UnsecureS3Bucket (line 5-15)",
            "resource": "AWS::S3::Bucket.UnsecureS3Bucket",
            "description": "Ensure S3 bucket has block public ACLS enabled",
            "module": "engine_iac",
            "tool": "Checkov"
        },
        {
            "id": "CKV_AWS_21",
            "custom_vuln_id": "CKV_AWS_21",
            "check_name": "Ensure the S3 bucket has versioning enabled",
            "check_class": "checkov.cloudformation.checks.resource.aws.S3Versioning",
            "severity": "high",
            "where": "/ms_artifact/cloudformation_test.template.yaml: AWS::S3::Bucket.UnsecureS3Bucket (line 5-15)",
            "resource": "AWS::S3::Bucket.UnsecureS3Bucket",
            "description": "Ensure the S3 bucket has versioning enabled",
            "module": "engine_iac",
            "tool": "Checkov"
        },
        {
            "id": "CKV_DOCKER_1",
            "custom_vuln_id": "CKV_DOCKER_1",
            "check_name": "Ensure port 22 is not exposed",
            "check_class": "checkov.dockerfile.checks.ExposePort22",
            "severity": "critical",
            "where": "/ms_artifact/Dockerfile: /Dockerfile.EXPOSE (line 4)",
            "resource": "/Dockerfile.EXPOSE",
            "description": "Ensure port 22 is not exposed",
            "module": "engine_iac",
            "tool": "Checkov"
        },
        {
            "id": "CKV_DOCKER_3",
            "custom_vuln_id": "CKV_DOCKER_3",
            "check_name": "Ensure that a user for the container has been created",
            "check_class": "checkov.dockerfile.checks.UserExists",
            "severity": "high",
            "where": "/ms_artifact/Dockerfile: /Dockerfile. (line 1-7)",
            "resource": "/Dockerfile.",
            "description": "Ensure that a user for the container has been created",
            "module": "engine_iac",
            "tool": "Checkov"
        },
        {
            "id": "CKV_AWS_144",
            "custom_vuln_id": "CKV_AWS_144",
            "check_name": "Ensure that S3 bucket has cross-region replication enabled",
            "check_class": "checkov.common.graph.checks_infra.base_check",
            "severity": "medium",
            "where": "/ms_artifact/terraform_test.tf: aws_s3_bucket.vulnerable_bucket (line 1-10)",
            "resource": "aws_s3_bucket.vulnerable_bucket",
            "description": "Ensure that S3 bucket has cross-region replication enabled",
            "module": "engine_iac",
            "tool": "Checkov"
        }
    ]
}`;
