import { OutputChannel } from "vscode";
import { exec } from "child_process";
import * as path from "path";

import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import { Finding } from "../../domain/model/Finding";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { ScanConfigurationService } from "../config/ScanConfigurationService";
import { ISeverityCounts } from "../../domain/model/mappers/Mappers";
import ContainerEngineManager from "../helper/ContainerEngineManager";
import { ScannerImageManager } from "../helper/ScannerImageManager";
import { BaseScannerHelper } from "../helper/BaseScannerHelper";
import { ScanContextMapper } from "../mappers/ScanContextMapper";
import { MetricsService } from "../services/MetricsService";
import { DockerService } from "../services/DockerService";
import { ErrorHandlingService } from "../services/ErrorHandlingService";

export class ImageScanner implements IScannerGateway {
  private metricsHelper = new MetricsService();
  private dockerErrorHandler = new DockerService();
  private networkErrorHandler = new ErrorHandlingService();
  async scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    containerImageName: string,
    toolVersion: string,
    containerEnginePath: string,
    scanLoader: any
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
      let imageTarPath: string = "";

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
            "engine_container",
            this.metricsHelper,
            outputChannel,
            resolve
          );
          return;
        }

        imageTarPath = ContainerEngineManager.createTemporaryImagePath(elementToScan);

        const exportSuccess = await ContainerEngineManager.exportImageToTar(elementToScan, imageTarPath);
        if (!exportSuccess) {
          await BaseScannerHelper.handleScanFailure(
            elementToScan,
            new Error(`Failed to export image ${elementToScan}`),
            "image export",
            "engine_container",
            this.metricsHelper,
            outputChannel,
            resolve
          );
          return;
        }

        outputChannel.appendLine(`Image exported successfully to ${imageTarPath}`);

        if (scanLoader) {
          scanLoader.start(`Image: ${elementToScan}`);
        }
        const imageTarName = path.basename(imageTarPath);

        const normalizedTarPath = ContainerEngineManager.normalizePathForDocker(imageTarPath);
        const versionEnv = toolVersion ? `-e ENGINE_VERSION=${toolVersion}` : '';
        const customConfigPath = ScanConfigurationService.getCustomRemoteConfigPath();
        const remoteConfigVolume = customConfigPath
          ? `-v "${ContainerEngineManager.normalizePathForDocker(customConfigPath)}:/ms_remote_config"`
          : '';
        const remoteConfigRepo = customConfigPath ? 'ms_remote_config' : 'docker_default_remote_config';
        const containerCommand = `${containerEnginePath} run --rm ${versionEnv} ${remoteConfigVolume} -v "${normalizedTarPath}:/tmp/${imageTarName}" ${containerImageName} sh -c "devsecops-engine-tools --platform_devops local --remote_config_source local --remote_config_repo ${remoteConfigRepo} --module engine_container --tool trivy --image_to_scan /tmp/${imageTarName} --context true"`;

        const cleanupImageTar = () => {
          if (imageTarPath) {
            ContainerEngineManager.removeFile(imageTarPath).catch(console.error);
          }
        };

        const timeout = BaseScannerHelper.createScanTimeout(
          outputChannel,
          this.metricsHelper,
          elementToScan,
          "engine_container",
          () => resolve(new ScannerRes(false, [], null)),
          cleanupImageTar
        );

        const debugMode = ScanConfigurationService.getDebugMode();

        const childProcess = exec(containerCommand, (error, stdout, stderr) => {
          clearTimeout(timeout);
          cleanupImageTar();

          if (error) {
            this.errorHandler(outputChannel, error, stderr, containerImageName, toolVersion);
          }

          if (stdout) {
            // Use centralized context extraction
            const result = ScanContextMapper.extractContextFromOutput(stdout, 'image');
            
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
            "engine_container",
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
            "during image scanning",
            "engine_container",
            this.metricsHelper,
            outputChannel,
            resolve,
            () => {
              if (imageTarPath) {
                ContainerEngineManager.removeFile(imageTarPath).catch(console.error);
              }
            }
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
