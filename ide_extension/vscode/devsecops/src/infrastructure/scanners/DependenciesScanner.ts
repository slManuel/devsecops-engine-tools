import { OutputChannel } from "vscode";
import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { Finding } from "../../domain/model/Finding";
import { ScanConfigurationService } from "../config/ScanConfigurationService";
import { exec } from "child_process";
import { ISeverityCounts } from "../../domain/model/mappers/Mappers";
import { ScannerImageManager } from "../helper/ScannerImageManager";
import ContainerEngineManager from "../helper/ContainerEngineManager";
import { BaseScannerHelper } from "../helper/BaseScannerHelper";
import { ScanContextMapper } from "../mappers/ScanContextMapper";
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
    const startTime = BaseScannerHelper.initializeScan(
      outputChannel,
      this.metricsHelper,
      this.dockerErrorHandler,
      this.networkErrorHandler
    );

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
          outputChannel,
          (message) => this.metricsHelper.captureOnly(message)
        );

        if (!scannerImageAvailable) {
          await BaseScannerHelper.handleScanFailure(
            elementToScan,
            new Error("Failed to ensure scanner image is available"),
            "scanner image availability",
            "engine_dependencies",
            this.metricsHelper,
            outputChannel,
            resolve,
            undefined,
            startTime
          );
          return;
        }

        if (scanLoader) {
          scanLoader.start(`Dependencies for: ${elementToScan.split('/').pop() || elementToScan}`);
        }

        const timeout = BaseScannerHelper.createScanTimeout(
          outputChannel,
          this.metricsHelper,
          elementToScan,
          "engine_dependencies",
          () => resolve(new ScannerRes(false, [], null)),
          startTime
        );

        if ((dependenciesTool === "xray" || dependenciesTool === "dependency_check") && !dependenciesToken) {
          clearTimeout(timeout);
          outputChannel.appendLine(`No Dependencies Token provided for ${dependenciesTool} tool\n Go to Settings to configure it!`);
          await BaseScannerHelper.handleScanFailure(
            elementToScan,
            new Error("No dependencies token provided"),
            "dependency token validation",
            "engine_dependencies",
            this.metricsHelper,
            outputChannel,
            resolve,
            undefined,
            startTime
          );
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
        const versionEnv = toolVersion ? `-e ENGINE_VERSION=${toolVersion}` : '';
        const customConfigPath = ScanConfigurationService.getCustomRemoteConfigPath();
        const remoteConfigVolume = customConfigPath
          ? `-v "${ContainerEngineManager.normalizePathForDocker(customConfigPath)}:/app/ms_remote_config"`
          : '';
        const remoteConfigRepo = customConfigPath ? 'ms_remote_config' : 'docker_default_remote_config';
        const containerCommand = `${containerEnginePath} run --rm ${versionEnv} ${remoteConfigVolume} ${dependencyCheckDatabaseVolume} -v ${normalizedElementPath}:/ms_artifact ${containerImageName} sh -c "devsecops-engine-tools --platform_devops local --remote_config_source local --xray_mode ${xrayMode} --remote_config_repo ${remoteConfigRepo} --module engine_dependencies --tool ${dependenciesTool} ${tokenParameter} --folder_path /ms_artifact --context true"`;

        const debugMode = ScanConfigurationService.getDebugMode();

        const childProcess = exec(containerCommand, (error, stdout, stderr) => {
          clearTimeout(timeout);
          if (error) {
            this.errorHandler(outputChannel, error, stderr, containerImageName, toolVersion);
          }

          if (stdout) {
            // Use centralized context extraction
            const result = ScanContextMapper.extractContextFromOutput(stdout, 'dependencies');
            
            if (result.success) {
              findings = result.findings;
              severityCounts = result.severityCounts;
              scanResult = true;
              this.metricsHelper.captureLog(outputChannel, `Successfully extracted context data with ${findings.length} findings`);
            } else {
              outputChannel.appendLine(result.errorMessage || "No context data found in scanner output");
              scanResult = false;
            }

            // Handle debug output
            BaseScannerHelper.handleDebugOutput(outputChannel, debugMode, stderr, result.normalOutput);
          } else {
            outputChannel.appendLine("Container command completed with no output");
          }

          void BaseScannerHelper.completeScan(
            elementToScan,
            findings,
            severityCounts,
            scanResult,
            "engine_dependencies",
            this.metricsHelper,
            outputChannel,
            resolve,
            startTime
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
            "during dependencies scanning",
            "engine_dependencies",
            this.metricsHelper,
            outputChannel,
            resolve,
            undefined,
            startTime
          );
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
