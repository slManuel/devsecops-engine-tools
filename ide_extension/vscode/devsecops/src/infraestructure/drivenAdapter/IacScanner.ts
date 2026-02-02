import { OutputChannel } from "vscode";
import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import OutputManager from "../helper/OutputManager";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { Finding } from "../../domain/model/Finding";
import { exec, execSync } from "child_process";
import { IIacContext, ISeverityCounts, Mappers } from "../../domain/model/mappers/Mappers";
import { ScannerImageManager } from "../helper/ScannerImageManager";
import { ScannerMetricsHelper } from "../helper/ScannerMetricsHelper";
import { DockerErrorHandler } from "../helper/DockerErrorHandler";
import { NetworkErrorHandler } from "../helper/NetworkErrorHandler";

export class IacScanner implements IScannerGateway {
  private metricsHelper = new ScannerMetricsHelper();
  private dockerErrorHandler = new DockerErrorHandler();
  private networkErrorHandler = new NetworkErrorHandler();
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
    this.metricsHelper.clearLogs();
    this.dockerErrorHandler.reset();
    this.networkErrorHandler.reset();

    return new Promise(async (resolve, _reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];
      let severityCounts: ISeverityCounts | null = null;

      try {
        const scannerImageAvailable = await ScannerImageManager.ensureScannerImageExists(
          containerEnginePath,
          containerImageName,
          toolVersion,
          outputChannel,
          (message) => this.metricsHelper.captureOnly(message)
        );

        if (!scannerImageAvailable) {
          this.metricsHelper.captureLog(outputChannel, "Failed to ensure scanner image is available. Aborting scan.");
          await this.collectFailedScanMetrics(elementToScan);
          resolve(new ScannerRes(false, [], null));
          return;
        }

        if (scanLoader) {
          scanLoader.start(`Infrastructure as Code for: ${elementToScan.split('/').pop()} `);
        }

        const timeout = setTimeout(async () => {
          outputChannel.appendLine("Scan timed out after 10 minutes");
          outputChannel.appendLine("Container command may be hanging. Check container engine configuration.");
          this.metricsHelper.captureLog(outputChannel, "Scan timed out after 10 minutes");
          await this.collectFailedScanMetrics(elementToScan);
          resolve(new ScannerRes(false, [], null));
        }, 600000);

        const containerCommand = `${containerEnginePath} run --rm -v ${elementToScan}:/ms_artifact ${containerImageName}:${toolVersion} sh -c "devsecops-engine-tools --platform_devops local --remote_config_source local --remote_config_repo docker_default_remote_config --module engine_iac --tool ${iacTool}${iacTool === "kics" ? " --platform openapi" : ""} --folder_path /ms_artifact --context true"`;

        const childProcess = exec(containerCommand, (error, stdout, stderr) => {
          clearTimeout(timeout);
          if (error) {
            this.errorHandler(outputChannel, error, stderr, containerImageName, toolVersion);
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
                severityCounts = this.calculateRawSeverityCounts(contextJson.iac_context);
                scanResult = true;
                outputChannel.appendLine(
                  `Successfully extracted context data with ${findings.length} findings`
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

          this.metricsHelper.collectAndstoreMetricsData(
            elementToScan,
            findings,
            severityCounts,
            scanResult,
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
        await this.collectFailedScanMetrics(elementToScan);
        resolve(new ScannerRes(false, [], null));
      }
    });
  }

  async getRuleCode(
    ruleId: string,
    finding: Finding,
    containerEnginePath: string,
    containerImageName: string,
    toolVersion: string
  ): Promise<Finding> {
    if (!ruleId.includes('_BC_')) {
      return finding;
    }

    let secret = "";
    let url = "";
    try {
      const { execSync } = require("child_process");
      secret = execSync(
        `${containerEnginePath} run --rm ${containerImageName}:${toolVersion} sh -c 'echo $DEFECT_DOJO_SECRET'`
      ).toString().trim();
      url = execSync(
        `${containerEnginePath} run --rm ${containerImageName}:${toolVersion} sh -c 'echo $CONTEXT_MANAGER'`
      ).toString().trim();
    } catch (error) {
      console.error("Error obtaining context manager", error);
      return finding;
    }

    try {
      url = `${url}/${ruleId}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': secret
        }
      });

      if (response.status === 200) {
        const rulePrint = (await response.text()).replace(/\\n/g, '\n');
        finding.setValidationRuleCode(rulePrint);
      }
    } catch (error) {
      console.error(`Error fetching rule code for ${ruleId}:`, error);
    }

    return finding;
  }


  private errorHandler(
    outputChannel: OutputChannel,
    error: Error,
    stderr: string,
    containerImageName: string,
    toolVersion: string
  ): void {
    const errorContext = {
      imageTag: `${containerImageName}:${toolVersion}`,
      containerImageName,
      toolVersion
    };

    // Create log capture callback to ensure error messages are captured for metrics
    const logCapture = (message: string) => {
      this.metricsHelper.captureOnly(message);
    };

    // Use DockerErrorHandler for known Docker errors
    this.dockerErrorHandler.handle(error.message, outputChannel, errorContext, logCapture);

    // Also check stderr for additional error patterns
    if (stderr) {
      this.dockerErrorHandler.handle(stderr, outputChannel, errorContext, logCapture);
      this.networkErrorHandler.handle(stderr, outputChannel, errorContext, logCapture);
    }
  }

  /**
   * Helper method to collect metrics for failed scan scenarios.
   * Eliminates code duplication across error handling paths.
   */
  private async collectFailedScanMetrics(elementToScan: string): Promise<void> {
    await this.metricsHelper.collectAndstoreMetricsData(
      elementToScan,
      [],
      null,
      false,
      "engine_iac"
    );
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
