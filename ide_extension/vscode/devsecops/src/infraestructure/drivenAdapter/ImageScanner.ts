import { OutputChannel } from "vscode";
import OutputManager from "../helper/OutputManager";
import { exec } from "child_process";
import * as path from "path";

import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import { Finding } from "../../domain/model/Finding";
import { ScannerRes } from "../../domain/model/ScannerRes";
import {
  IImageScanContext,
  Mappers,
} from "../../domain/model/mappers/Mappers";
import ContainerEngineManager from "../helper/ContainerEngineManager";
import { ScannerImageManager } from "../helper/ScannerImageManager";

export class ImageScanner implements IScannerGateway {
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

    return new Promise(async (resolve, _reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];
      let imageTarPath: string | null = null;

      try {
        const scannerImageAvailable = await ScannerImageManager.ensureScannerImageExists(
          containerEnginePath,
          containerImageName,
          toolVersion,
          outputChannel
        );

        if (!scannerImageAvailable) {
          outputChannel.appendLine("Failed to ensure scanner image is available. Aborting scan.");
          resolve(new ScannerRes(false, []));
          return;
        }

        imageTarPath = ContainerEngineManager.createTemporaryImagePath(elementToScan);

        const exportSuccess = await ContainerEngineManager.exportImageToTar(elementToScan, imageTarPath);
        if (!exportSuccess) {
          outputChannel.appendLine(`Failed to export image ${elementToScan}`);
          resolve(new ScannerRes(false, []));
          return;
        }

        outputChannel.appendLine(`Image exported successfully to ${imageTarPath}`);

        // Call scanLoader after all Docker operations (scanner image check + image export) are complete
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
          resolve(new ScannerRes(false, []));
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

                scanResult = true;
                outputChannel.appendLine(`Successfully extracted context data with ${findings.length} findings`);
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
            outputChannel.appendLine(`Found ${findings.length} issues in scan`);
          } else {
            outputChannel.appendLine("Container command completed with no output");
          }

          resolve(new ScannerRes(scanResult, findings));
        });

        childProcess.on("exit", (code) => {
          if (code !== 0 && code !== null) {
            outputChannel.appendLine(`Container process exited with code ${code}`);
          }
        });

      } catch (error) {
        outputChannel.appendLine(`Error during image scanning: ${error instanceof Error ? error.message : String(error)}`);
        if (imageTarPath) {
          ContainerEngineManager.removeFile(imageTarPath).catch(console.error);
        }
        resolve(new ScannerRes(false, []));
      }
    });
  }
}
