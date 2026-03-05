import { OutputChannel } from "vscode";
import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import OutputManager from "../helper/OutputManager";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { Finding } from "../../domain/model/Finding";
import { ScanConfigurationService } from "../config/ScanConfigurationService";
import { exec } from "child_process";
import { IDependenciesScanContext, ISeverityCounts, Mappers } from "../../domain/model/mappers/Mappers";
import { ScannerImageManager } from "../helper/ScannerImageManager";
import ContainerEngineManager from "../helper/ContainerEngineManager";
import { MetricsService } from "../services/MetricsService";
import { DockerService } from "../services/DockerService";
import { ErrorHandlingService } from "../services/ErrorHandlingService";

export class DependenciesScanner implements IScannerGateway {
  private metricsHelper = new MetricsService();
  private dockerErrorHandler = new DockerService();
  private networkErrorHandler = new ErrorHandlingService();

  async scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    containerImageName: string,
    toolVersion: string,
    containerEnginePath: string,
    dependenciesToken: string,
    xrayMode: string,
    dependenciesTool: string,
    dependencyCheckDatabase: string,
    scanLoader: any
  ): Promise<ScannerRes> {
    outputChannel.clear();
    outputChannel.show();

    this.metricsHelper.clearLogs();
    this.dockerErrorHandler.reset();
    this.networkErrorHandler.reset();

    return new Promise((resolve, _reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];
      let severityCounts: ISeverityCounts | null = null;
      let dependencyCheckDatabaseVolume = "";

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
          this.metricsHelper.captureLog(outputChannel, "Failed to ensure scanner image is available. Aborting scan.");
          await this.collectFailedScanMetrics(elementToScan);
          resolve(new ScannerRes(false, [], null));
          return;
        }

        if (scanLoader) {
          scanLoader.start(`Dependencies for: ${elementToScan.split('/').pop() || elementToScan}`);
        }

        const scanTimeout = ScanConfigurationService.getScanTimeout();
        const timeoutMinutes = Math.floor(scanTimeout / 60000);
        const timeout = setTimeout(() => {
          outputChannel.appendLine(`Scan timed out after ${timeoutMinutes} minutes`);
          outputChannel.appendLine(
            "Container command may be hanging. Check container engine configuration."
          );
          this.metricsHelper.captureLog(outputChannel, `Scan timed out after ${timeoutMinutes} minutes`);
          void this.collectFailedScanMetrics(elementToScan).then(() => {
            resolve(new ScannerRes(false, [], null));
          }).catch((error) => {
            this.metricsHelper.captureError(outputChannel, error, "collecting timeout metrics");
            resolve(new ScannerRes(false, [], null));
          });
        }, scanTimeout);

        if ((dependenciesTool === "xray" || dependenciesTool === "dependency_check") && !dependenciesToken) {
          outputChannel.appendLine(`No Dependencies Token provided for ${dependenciesTool} tool\n Go to Settings to configure it!`);
          await this.collectFailedScanMetrics(elementToScan);
          resolve(new ScannerRes(false, [], null));
          return;
        }

        if (dependenciesTool === "dependency_check" && dependencyCheckDatabase) {
          const normalizedDbPath = ContainerEngineManager.normalizePathForDocker(dependencyCheckDatabase);
          dependencyCheckDatabaseVolume = `-v ${normalizedDbPath}:/root/dependency-check`;
        }

        let tokenParameter = "";
        if (dependenciesToken && (dependenciesTool === "xray" || dependenciesTool === "dependency_check")) {
          tokenParameter = `--token_engine_dependencies ${dependenciesToken}`;
        }

        const normalizedElementPath = ContainerEngineManager.normalizePathForDocker(elementToScan);
        const containerCommand = `${containerEnginePath} run --rm ${dependencyCheckDatabaseVolume} -v ${normalizedElementPath}:/ms_artifact ${containerImageName}:${toolVersion} sh -c "devsecops-engine-tools --platform_devops local --remote_config_source local --xray_mode ${xrayMode} --remote_config_repo docker_default_remote_config --module engine_dependencies --tool ${dependenciesTool} ${tokenParameter} --folder_path /ms_artifact --context true"`;

        const debugMode = ScanConfigurationService.getDebugMode();

        const childProcess = exec(containerCommand, (error, stdout, stderr) => {
          clearTimeout(timeout);
          if (error) {
            this.errorHandler(outputChannel, error, stderr, containerImageName, toolVersion);
          }

          // Show stderr in debug mode
          if (debugMode && stderr) {
            outputChannel.appendLine("\n📋 STDERR OUTPUT:");
            outputChannel.appendLine(stderr);
          }

          if (stdout) {
            let contextJson: { dependencies_context: IDependenciesScanContext[] } | null = null;
            let normalOutput = stdout;

            const contextRegex =
              /===== BEGIN CONTEXT OUTPUT =====\s*([\s\S]*?)\s*===== END CONTEXT OUTPUT =====/;
            const match = stdout.match(contextRegex);

            if (match && match[1]) {
              try {
                contextJson = JSON.parse(match[1].trim()) as { dependencies_context: IDependenciesScanContext[] };

                normalOutput = stdout.replace(contextRegex, "");

                findings = contextJson.dependencies_context.map(
                  (finding: IDependenciesScanContext) =>
                    Mappers.mapDependenciesScanContextToFinding(finding)
                );

                severityCounts = this.calculateRawSeverityCounts(contextJson.dependencies_context);

                scanResult = true;
                this.metricsHelper.captureLog(outputChannel,
                  `Successfully extracted context data with ${findings.length} findings`
                );
              } catch (jsonError: unknown) {
                let errorMsg = "Unknown error";
                if (jsonError instanceof Error) {
                  errorMsg = jsonError.message;
                } else if (typeof jsonError === "string") {
                  errorMsg = jsonError;
                }
                outputChannel.appendLine(
                  `Error parsing context JSON: ${errorMsg}`
                );
                outputChannel.appendLine("Raw context data:");
                outputChannel.appendLine(match[1]);
              }
            } else {
              outputChannel.appendLine(
                "No context data found in scanner output. Using default context."
              );
              scanResult = false;
            }

            if (debugMode) {
              const cleanedOutput = OutputManager.removeAnsiEscapeCodes(normalOutput);
              outputChannel.appendLine("\n📄 SCAN OUTPUT:");
              outputChannel.appendLine(cleanedOutput);
            }
            this.metricsHelper.captureLog(outputChannel, `Found ${findings.length} issues in scan`);
          } else {
            outputChannel.appendLine("Container command completed with no output");
          }

          void this.metricsHelper.collectAndstoreMetricsData(
            elementToScan,
            findings,
            severityCounts,
            scanResult,
            "engine_dependencies"
          ).catch((error) => {
            this.metricsHelper.captureError(outputChannel, error, "storing metrics");
          });

          resolve(new ScannerRes(scanResult, findings, severityCounts));
        });

        childProcess.on("exit", (code) => {
          if (code !== 0 && code !== null) {
            this.metricsHelper.captureExitCode(outputChannel, code);
          }
        });

        } catch (error) {
          this.metricsHelper.captureError(outputChannel, error, "during dependencies scanning");
          await this.collectFailedScanMetrics(elementToScan);
          resolve(new ScannerRes(false, [], null));
        }
      })();
    });
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

    const logCapture = (message: string) => {
      this.metricsHelper.captureOnly(message);
    };

    this.dockerErrorHandler.handle(error.message, outputChannel, errorContext, logCapture);

    if (stderr) {
      this.dockerErrorHandler.handle(stderr, outputChannel, errorContext, logCapture);
      this.networkErrorHandler.handle(stderr, outputChannel, errorContext, logCapture);
    }
  }

  private async collectFailedScanMetrics(elementToScan: string): Promise<void> {
    await this.metricsHelper.collectAndstoreMetricsData(
      elementToScan,
      [],
      null,
      false,
      "engine_dependencies"
    );
  }

  private calculateRawSeverityCounts(contexts: IDependenciesScanContext[]): ISeverityCounts {
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
