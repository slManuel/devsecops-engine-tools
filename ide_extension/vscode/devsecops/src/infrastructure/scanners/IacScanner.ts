import { OutputChannel } from "vscode";
import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { Finding } from "../../domain/model/Finding";
import { ScanConfigurationService } from "../config/ScanConfigurationService";
import { exec, execSync } from "child_process";
import { ISeverityCounts } from "../../domain/model/mappers/Mappers";
import { ScannerImageManager } from "../helper/ScannerImageManager";
import ContainerEngineManager from "../helper/ContainerEngineManager";
import { BaseScannerHelper } from "../helper/BaseScannerHelper";
import { ScanContextMapper } from "../mappers/ScanContextMapper";
import { MetricsService } from "../services/MetricsService";
import { DockerService } from "../services/DockerService";
import { ErrorHandlingService } from "../services/ErrorHandlingService";

export class IacScanner implements IScannerGateway {
  private metricsHelper = new MetricsService();
  private dockerErrorHandler = new DockerService();
  private networkErrorHandler = new ErrorHandlingService();
  async scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    containerImageName: string,
    iacTool: string,
    toolVersion: string,
    containerEnginePath: string,
    scanLoader?: any
  ): Promise<ScannerRes> {
    BaseScannerHelper.initializeScan(
      outputChannel,
      this.metricsHelper,
      this.dockerErrorHandler,
      this.networkErrorHandler
    );

    return new Promise((resolve, _reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];
      let severityCounts: ISeverityCounts | null = null;

      void (async () => {
        try {
          const scannerImageAvailable = await ScannerImageManager.ensureScannerImageExists(
            containerEnginePath,
            containerImageName,
            toolVersion,
            outputChannel,
            (message) => this.metricsHelper.captureOnly(message)
          );

          if (!scannerImageAvailable) {
            await BaseScannerHelper.handleScanFailure(
              elementToScan,
              new Error("Failed to ensure scanner image is available"),
              "scanner image availability",
              "engine_iac",
              this.metricsHelper,
              outputChannel,
              resolve
            );
            return;
          }

          if (scanLoader) {
            scanLoader.start(`Infrastructure as Code for: ${elementToScan.split('/').pop()} `);
          }

          const timeout = BaseScannerHelper.createScanTimeout(
            outputChannel,
            this.metricsHelper,
            elementToScan,
            "engine_iac",
            () => resolve(new ScannerRes(false, [], null))
          );

          const normalizedElementPath = ContainerEngineManager.normalizePathForDocker(elementToScan);
          const containerCommand = `${containerEnginePath} run --rm -v ${normalizedElementPath}:/ms_artifact ${containerImageName}:${toolVersion} sh -c "devsecops-engine-tools --platform_devops local --remote_config_source local --remote_config_repo docker_default_remote_config --module engine_iac --tool ${iacTool}${iacTool === "kics" ? " --platform openapi" : ""} --folder_path /ms_artifact --context true"`;

          const debugMode = ScanConfigurationService.getDebugMode();

          const childProcess = exec(containerCommand, (error, stdout, stderr) => {
            clearTimeout(timeout);
            
            if (error) {
              this.errorHandler(outputChannel, error, stderr, containerImageName, toolVersion);
            }

            if (stdout) {
              // Use centralized context extraction
              const result = ScanContextMapper.extractContextFromOutput(stdout, 'iac');
              
              if (result.success) {
                findings = result.findings;
                severityCounts = result.severityCounts;
                scanResult = true;
                outputChannel.appendLine(`Successfully extracted context data with ${findings.length} findings`);
              } else {
                outputChannel.appendLine(result.errorMessage || "No context data found in scanner output");
                if (result.errorMessage?.includes("Error parsing")) {
                  outputChannel.appendLine("Raw context data available in debug mode");
                }
                scanResult = false;
              }

              // Handle debug output
              BaseScannerHelper.handleDebugOutput(outputChannel, debugMode, stderr, result.normalOutput);
            } else {
              outputChannel.appendLine("Docker command completed with no output");
            }

            void BaseScannerHelper.completeScan(
              elementToScan,
              findings,
              severityCounts,
              scanResult,
              "engine_iac",
              this.metricsHelper,
              outputChannel,
              resolve
            );
          });

          childProcess.on("exit", (code) => {
            if (code !== 0 && code !== null) {
              this.metricsHelper.captureExitCode(outputChannel, code);
            }
          });

        } catch (error) {
          await BaseScannerHelper.handleScanFailure(
            elementToScan,
            error,
            "during IaC scanning",
            "engine_iac",
            this.metricsHelper,
            outputChannel,
            resolve
          );
        }
      })();
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
    this.metricsHelper.handleScanError(
      error,
      stderr,
      containerImageName,
      toolVersion,
      outputChannel,
      this.dockerErrorHandler,
      this.networkErrorHandler
    );
  }
}
