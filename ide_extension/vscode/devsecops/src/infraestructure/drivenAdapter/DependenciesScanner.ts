import { OutputChannel } from "vscode";
import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import OutputManager from "../helper/OutputManager";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { Finding } from "../../domain/model/Finding";
import { exec } from "child_process";
import { IDependenciesScanContext, ISeverityCounts, Mappers } from "../../domain/model/mappers/Mappers";
import { ScannerImageManager } from "../helper/ScannerImageManager";
import { ScannerMetricsHelper } from "../helper/ScannerMetricsHelper";
import { DockerErrorHandler, ErrorContext } from "../helper/DockerErrorHandler";

export class DependenciesScanner implements IScannerGateway {
  private metricsHelper = new ScannerMetricsHelper();
  private dockerErrorHandler = new DockerErrorHandler();

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

    return new Promise(async (resolve, _reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];
      let severityCounts: ISeverityCounts | null = null;
      let dependencyCheckDatabaseVolume = "";

      try {
        this.dockerErrorHandler.reset();

        const scannerImageAvailable = await ScannerImageManager.ensureScannerImageExists(
          containerEnginePath,
          containerImageName,
          toolVersion,
          outputChannel
        );

        if (!scannerImageAvailable) {
          // Mandar error al metrics con docker error handler
          this.metricsHelper.captureLog(outputChannel, "Failed to ensure scanner image is available. Aborting scan.");
          resolve(new ScannerRes(false, [], null));
          return;
        }

        if (scanLoader) {
          scanLoader.start(`Dependencies for: ${elementToScan.split('/').pop() || elementToScan}`);
        }

        const timeout = setTimeout(() => {
          outputChannel.appendLine("Scan timed out after 10 minutes");
          outputChannel.appendLine(
            "Container command may be hanging. Check container engine configuration."
          );
          resolve(new ScannerRes(false, [], null));
        }, 12000000);

        if ((dependenciesTool === "xray" || dependenciesTool === "dependency_check") && !dependenciesToken) {
          outputChannel.appendLine(`No Dependencies Token provided for ${dependenciesTool} tool\n Go to Settings to configure it!`);
          resolve(new ScannerRes(false, [], null));
          return;
        }

        if (dependenciesTool === "dependency_check" && dependencyCheckDatabase) {
          dependencyCheckDatabaseVolume = `-v ${dependencyCheckDatabase}:/root/dependency-check`;
        }

        let tokenParameter = "";
        if (dependenciesToken && (dependenciesTool === "xray" || dependenciesTool === "dependency_check")) {
          tokenParameter = `--token_engine_dependencies ${dependenciesToken}`;
        }

        const containerCommand = `${containerEnginePath} run --rm ${dependencyCheckDatabaseVolume} -v ${elementToScan}:/ms_artifact ${containerImageName}:${toolVersion} sh -c "devsecops-engine-tools --platform_devops local --remote_config_source local --xray_mode ${xrayMode} --remote_config_repo docker_default_remote_config --module engine_dependencies --tool ${dependenciesTool} ${tokenParameter} --folder_path /ms_artifact --context true"`;

        const childProcess = exec(containerCommand, (error, stdout, stderr) => {
          clearTimeout(timeout);
          if (error) {
            const errorContext: ErrorContext = {
              imageTag: `${containerImageName}:${toolVersion}`,
              containerImageName,
              toolVersion
            };

            // Use DockerErrorHandler for known Docker errors y eviar al metrics
            this.dockerErrorHandler.handle(error.message, outputChannel, errorContext);

            // Also check stderr for additional error patterns
            if (stderr) {
              this.dockerErrorHandler.handle(stderr, outputChannel, errorContext);
            }
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

            const cleanedOutput =
              OutputManager.removeAnsiEscapeCodes(normalOutput);

            outputChannel.appendLine("SCAN OUTPUT:");
            outputChannel.appendLine(cleanedOutput);
            this.metricsHelper.captureLog(outputChannel, `Found ${findings.length} issues in scan`);
          } else {
            outputChannel.appendLine("Container command completed with no output");
          }

          this.metricsHelper.collectAndstoreMetricsData(
            elementToScan,
            findings,
            severityCounts,
            scanResult,
            "engine_dependencies"
          );

          resolve(new ScannerRes(scanResult, findings, severityCounts));
        });

        childProcess.on("exit", (code) => {
          if (code !== 0 && code !== null) {
            this.metricsHelper.captureExitCode(outputChannel, code);
          }
        });

      } catch (error) {
        this.metricsHelper.captureError(outputChannel, error, "during dependencies scanning");
        resolve(new ScannerRes(false, [], null));
      }
    });
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
