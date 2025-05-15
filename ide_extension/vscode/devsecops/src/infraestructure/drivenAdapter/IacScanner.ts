import { OutputChannel } from "vscode";
import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import OutputManager from "../helper/OutputManager";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { Finding } from "../../domain/model/Finding";

import { exec } from "child_process";

export class IacScanner implements IScannerGateway {
  async scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    dockerImageName: string,
    toolVersion: string,
    dockerPath: string
  ): Promise<ScannerRes> {
    outputChannel.clear();
    outputChannel.show();
    return new Promise((resolve, reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];
      
      const timeout = setTimeout(() => {
        outputChannel.appendLine("Scan timed out after 2 minutes");
        outputChannel.appendLine("Docker command may be hanging. Check Docker configuration.");
        resolve(new ScannerRes(false, []));
      }, 120000);
      
      const dockerCommand = `${dockerPath} run --rm -v ${elementToScan}:/ms_artifact ${dockerImageName}:1.59.0 devsecops-engine-tools --platform_devops local --remote_config_repo docker_default_remote_config --module engine_iac --tool checkov --folder_path /ms_artifact --context true`;
      
      const childProcess = exec(
        dockerCommand,
        (error, stdout, stderr) => {
          clearTimeout(timeout);
          if (error) {
            outputChannel.appendLine(`Error executing Docker command: ${error.message}`);
            if (stderr.includes("Unable to find image")) {
              outputChannel.appendLine("Docker image not found. Attempting to download...");
            } else {
              outputChannel.appendLine(`Standard Error: ${stderr}`);
              outputChannel.appendLine("Attempting to process partial results...");
            }
          }
  
          if (stdout) {
            // Extract the context JSON from the output
            let contextJson = null;
            let normalOutput = stdout;
            
            // Use regex to extract everything between BEGIN CONTEXT OUTPUT and END CONTEXT OUTPUT markers
            const contextRegex = /===== BEGIN CONTEXT OUTPUT =====\s*([\s\S]*?)\s*===== END CONTEXT OUTPUT =====/;
            const match = stdout.match(contextRegex);
            
            if (match && match[1]) {
              // We have context JSON data
              try {
                contextJson = JSON.parse(match[1].trim());
                
                // Remove the context block from normal output
                normalOutput = stdout.replace(contextRegex, "");
                
                // Process the findings from the extracted JSON
                findings = contextJson.iac_context.map((finding: any) => {
                  return new Finding(
                    finding.id || "",
                    finding.custom_vuln_id || finding.id || "",
                    finding.check_name || "",
                    finding.check_class || "",
                    finding.severity || "unknown",
                    finding.where || "",
                    finding.resource || "",
                    finding.description || "",
                    finding.module || "engine_iac",
                    finding.tool || "Checkov"
                  );
                });
                
                scanResult = true;
                outputChannel.appendLine(`Successfully extracted context data with ${findings.length} findings`);
              } catch (jsonError) {
                outputChannel.appendLine(`Error parsing context JSON: ${jsonError}`);
                outputChannel.appendLine("Raw context data:");
                outputChannel.appendLine(match[1]);
              }
            } else {
              outputChannel.appendLine("No context data found in scanner output. Using default context.");
              scanResult = false;
            }
            
            // Display the normal output (with context section removed)
            const cleanedOutput = OutputManager.removeAnsiEscapeCodes(normalOutput);
            outputChannel.appendLine("SCAN OUTPUT:");
            outputChannel.appendLine(cleanedOutput);
            outputChannel.appendLine(`Found ${findings.length} issues in scan`);
          } else {
            outputChannel.appendLine("Docker command completed with no output");
          }
          
          resolve(new ScannerRes(scanResult, findings));
        }
      );
      
      childProcess.on('exit', (code) => {
        if (code !== 0 && code !== null) {
          outputChannel.appendLine(`Docker process exited with code ${code}`);
        }
      });
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