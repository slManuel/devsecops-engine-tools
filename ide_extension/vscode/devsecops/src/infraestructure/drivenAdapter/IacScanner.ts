import { OutputChannel } from "vscode";
import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import OutputManager from "../helper/OutputManager";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { Finding } from "../../domain/model/Finding";

import { exec, execSync } from "child_process";
import { IIacContext, ISeverityCounts, Mappers } from "../../domain/model/mappers/Mappers";
import { ScannerImageManager } from "../helper/ScannerImageManager";
import { ScannerMetricsHelper } from "../helper/ScannerMetricsHelper";

export class IacScanner implements IScannerGateway {
  private metricsHelper = new ScannerMetricsHelper();
  async scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    containerImageName: string,
    iacTool: string,
    toolVersion: string,
    containerEnginePath: string,
    scanLoader?: any
  ): Promise<ScannerRes> {
    outputChannel.show();
    
    // Initialize metrics collection
    this.metricsHelper.clearLogs();
    
    return new Promise(async (resolve, _reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];
      let severityCounts: ISeverityCounts | null = null;

      try {
        const scannerImageAvailable = await ScannerImageManager.ensureScannerImageExists(
          containerEnginePath,
          containerImageName,
          toolVersion,
          outputChannel
        );

        if (!scannerImageAvailable) {
          this.metricsHelper.captureLog(outputChannel, "Failed to ensure scanner image is available. Aborting scan.");
          resolve(new ScannerRes(false, [], null));
          return;
        }

        if (scanLoader) {
          scanLoader.start(`Infrastructure as Code for: ${elementToScan.split('/').pop()} `);
        }

        const timeout = setTimeout(() => {
          outputChannel.appendLine("Scan timed out after 10 minutes");
          outputChannel.appendLine("Container command may be hanging. Check container engine configuration.");
          resolve(new ScannerRes(false, [], null));
        }, 600000);

        const containerCommand = `${containerEnginePath} run --rm -v ${elementToScan}:/ms_artifact ${containerImageName}:${toolVersion} sh -c "devsecops-engine-tools --platform_devops local --remote_config_source local --remote_config_repo docker_default_remote_config --module engine_iac --tool ${iacTool}${iacTool === "kics" ? " --platform openapi" : ""} --folder_path /ms_artifact --context true"`;

        const childProcess = exec(containerCommand, (error, stdout, stderr) => {
          clearTimeout(timeout);
          if (error) {
            this.errorHandler(outputChannel, error, stderr);
          }

          if (stdout) {
            let contextJson: { iac_context: IIacContext[] } | null = null;
            let normalOutput = stdout;

            const contextRegex =
              /===== BEGIN CONTEXT OUTPUT =====\s*([\s\S]*?)\s*===== END CONTEXT OUTPUT =====/;
            const match = stdout.match(contextRegex);

            if (match && match[1]) {
              try {
                contextJson = JSON.parse(match[1].trim()) as { iac_context: IIacContext[] };

                normalOutput = stdout.replace(contextRegex, "");

                findings = contextJson.iac_context.map(
                  (finding: IIacContext) =>
                    Mappers.mapIacContextToFinding(finding)
                );

                // Calculate severity counts directly from context data
                severityCounts = this.calculateRawSeverityCounts(contextJson.iac_context);

                scanResult = true;
                outputChannel.appendLine(
                  `Successfully extracted context data with ${findings.length} findings`
                );
                
                outputChannel.appendLine(
                  `Severity counts: Critical: ${severityCounts.critical}, High: ${severityCounts.high}, Medium: ${severityCounts.medium}, Low: ${severityCounts.low}`
                );
              } catch (jsonError: unknown) {
                let errorMsg = "Unknown error";
                if (jsonError instanceof Error) {
                  errorMsg = jsonError.message;
                } else if (typeof jsonError === "string") {
                  errorMsg = jsonError;
                }
                outputChannel.appendLine(`Error parsing context JSON: ${errorMsg}`);
                outputChannel.appendLine("Raw context data:");
                outputChannel.appendLine(match[1]);
              }
            } else {
              outputChannel.appendLine(
                "No context data found in scanner output. Using default context."
              );
              scanResult = false;
            }

            const cleanedOutput = OutputManager.removeAnsiEscapeCodes(normalOutput);

            outputChannel.appendLine("SCAN OUTPUT:");
            outputChannel.appendLine(cleanedOutput);
            this.metricsHelper.captureLog(outputChannel, `Found ${findings.length} issues in scan`);
          } else {
            outputChannel.appendLine("Docker command completed with no output");
          }

          // Collect metrics before resolving
          this.metricsHelper.collectAndstoreMetricsData(
            elementToScan,
            findings,
            severityCounts,
            scanResult,
            outputChannel,
            "engine_iac"
          );

          resolve(new ScannerRes(scanResult, findings, severityCounts));
        });

        childProcess.on("exit", (code) => {
          if (code !== 0 && code !== null) {
            this.metricsHelper.captureExitCode(outputChannel, code);
          }
        });

      } catch (error) {
        this.metricsHelper.captureError(outputChannel, error, "during IaC scanning");
        resolve(new ScannerRes(false, [], null));
      }
    });
  }

  getRuleCode(
    dockerPath: string,
    containerImageName: string,
    toolVersion: string,
    ruleId: string,
    finding: Finding
  ): Finding {
    const containerCommand = `${dockerPath} run --rm ${containerImageName}:${toolVersion}  python3 rules_context_extract.py ${ruleId}`;
    const rulePrint = execSync(containerCommand, { encoding: "utf-8" }).trim();
    finding.setValidationRuleCode(rulePrint);
    return finding;
  }

  private errorHandler(outputChannel: OutputChannel, error: Error, stderr: string): void {
    outputChannel.appendLine(`Error: ${error.message}`);
    outputChannel.appendLine("Please check your container engine configuration and try again.");
    if (stderr.includes("Unable to find image")) {
      outputChannel.appendLine("Container image not found. Attempting to download...");
    } else {
      outputChannel.appendLine(`Standard Error: ${stderr}`);
      outputChannel.appendLine("Attempting to process partial results...");
    }
  }

  private calculateRawSeverityCounts(contexts: IIacContext[]): ISeverityCounts {
    let counts = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0
    };

    contexts.forEach((context) => {
      const severity = context.severity?.toLowerCase();

      if (severity === 'critical') {
        counts.critical++;
      } else if (severity === 'high') {
        counts.high++;
      } else if (severity === 'medium') {
        counts.medium++;
      } else if (severity === 'low') {
        counts.low++;
      }
    });

    return {
      critical: counts.critical.toString(),
      high: counts.high.toString(),
      medium: counts.medium.toString(),
      low: counts.low.toString()
    };
  }
}
