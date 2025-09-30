import { OutputChannel } from "vscode";
import OutputManager from "../helper/OutputManager";
import { exec } from "child_process";
import * as path from "path";

import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import { Finding } from "../../domain/model/Finding";
import { ScannerRes } from "../../domain/model/ScannerRes";
import {
  IImageScanContext,
  ISeverityCounts,
  Mappers,
} from "../../domain/model/mappers/Mappers";
import ContainerEngineManager from "../helper/ContainerEngineManager";
import { ScannerImageManager } from "../helper/ScannerImageManager";
import { ScannerMetricsHelper } from "../helper/ScannerMetricsHelper";

export class ImageScanner implements IScannerGateway {
  private metricsHelper = new ScannerMetricsHelper();
  async scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    containerImageName: string,
    toolVersion: string,
    containerEnginePath: string,
    scanLoader: any
  ): Promise<ScannerRes> {
    outputChannel.clear();
    outputChannel.show();

    this.metricsHelper.clearLogs();

    return new Promise(async (resolve, _reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];
      let severityCounts: ISeverityCounts | null = null;
      let imageTarPath: string = "";

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

        imageTarPath = ContainerEngineManager.createTemporaryImagePath(elementToScan);

        const exportSuccess = await ContainerEngineManager.exportImageToTar(elementToScan, imageTarPath);
        if (!exportSuccess) {
          this.metricsHelper.captureLog(outputChannel, `Failed to export image ${elementToScan}`);
          resolve(new ScannerRes(false, [], null));
          return;
        }

        outputChannel.appendLine(`Image exported successfully to ${imageTarPath}`);

        if (scanLoader) {
          scanLoader.start(`Image: ${elementToScan}`);
        }
        const imageTarName = path.basename(imageTarPath);

        const containerCommand = `${containerEnginePath} run --rm -v "${imageTarPath}:/tmp/${imageTarName}" ${containerImageName}:${toolVersion} sh -c "
          devsecops-engine-tools --platform_devops local --remote_config_source local --remote_config_repo docker_default_remote_config --module engine_container --tool trivy --image_to_scan /tmp/${imageTarName} --context true
        "`;

        const timeout = setTimeout(() => {
          outputChannel.appendLine("Scan timed out after 10 minutes");
          outputChannel.appendLine("Container command may be hanging. Check container engine configuration.");
          if (imageTarPath) {
            ContainerEngineManager.removeFile(imageTarPath).catch(console.error);
          }
          resolve(new ScannerRes(false, [], null));
        }, 600000);

        const childProcess = exec(containerCommand, (error, stdout, stderr) => {
          clearTimeout(timeout);

          if (imageTarPath) {
            ContainerEngineManager.removeFile(imageTarPath).catch(console.error);
          }

          if (error) {
            outputChannel.appendLine(`Error executing container command: ${error.message}`);
            if (stderr.includes("Unable to find image")) {
              outputChannel.appendLine("Scanner container image not found. Attempting to download...");
            } else {
              outputChannel.appendLine(`Standard Error: ${stderr}`);
            }
          }

          if (stdout) {
            let contextJson: { container_context: IImageScanContext[] } | null = null;
            let normalOutput = stdout;

            const contextRegex = /===== BEGIN CONTEXT OUTPUT =====\s*([\s\S]*?)\s*===== END CONTEXT OUTPUT =====/;
            const match = stdout.match(contextRegex);

            if (match && match[1]) {
              try {
                contextJson = JSON.parse(match[1].trim()) as { container_context: IImageScanContext[] };
                normalOutput = stdout.replace(contextRegex, "");

                findings = contextJson.container_context.map(
                  (finding: IImageScanContext) =>
                    Mappers.mapImageScanContextToFinding(finding)
                );

                severityCounts = this.calculateRawSeverityCounts(contextJson.container_context);

                scanResult = true;
                this.metricsHelper.captureLog(outputChannel, `Successfully extracted context data with ${findings.length} findings`);

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
              outputChannel.appendLine("No context data found in scanner output. Using default context.");
              scanResult = false;
            }

            const cleanedOutput = OutputManager.removeAnsiEscapeCodes(normalOutput);
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
            "engine_container"
          );

          resolve(new ScannerRes(scanResult, findings, severityCounts));
        });

        childProcess.on("exit", (code) => {
          if (code !== 0 && code !== null) {
            this.metricsHelper.captureExitCode(outputChannel, code);
          }
        });

      } catch (error) {
        this.metricsHelper.captureError(outputChannel, error, "during image scanning");
        if (imageTarPath) {
          ContainerEngineManager.removeFile(imageTarPath).catch(console.error);
        }
        resolve(new ScannerRes(false, [], null));
      }
    });
  }

  private calculateRawSeverityCounts(contexts: IImageScanContext[]): ISeverityCounts {
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
