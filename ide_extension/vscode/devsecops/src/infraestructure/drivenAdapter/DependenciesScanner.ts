import { OutputChannel } from "vscode";
import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import OutputManager from "../helper/OutputManager";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { Finding } from "../../domain/model/Finding";
import { exec } from "child_process";
import { IDependenciesScanContext, Mappers } from "../../domain/model/mappers/Mappers";
import { ScannerImageManager } from "../helper/ScannerImageManager";

export class DependenciesScanner implements IScannerGateway {
  async scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    containerImageName: string,
    toolVersion: string,
    containerEnginePath: string,
    dependenciesToken: string,
    xrayMode: string,
    dependenciesTool: string,
    dependencyCheckDatabase: string
  ): Promise<ScannerRes> {
    outputChannel.clear();
    outputChannel.show();

    return new Promise(async (resolve, _reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];
      let dependencyCheckDatabaseVolume = "";

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

        const timeout = setTimeout(() => {
          outputChannel.appendLine("Scan timed out after 10 minutes");
          outputChannel.appendLine(
            "Container command may be hanging. Check container engine configuration."
          );
          resolve(new ScannerRes(false, []));
        }, 12000000);

        if (!dependenciesToken) {
          outputChannel.appendLine("No Dependencies Token to scan provided\n Go to Settings to configure it!");
          resolve(new ScannerRes(false, []));
          return;
        }
        if (dependenciesTool === "dependency_check" && dependencyCheckDatabase) {
            dependencyCheckDatabaseVolume = `-v ${dependencyCheckDatabase}:/root/dependency-check`;
        }

      const containerCommand = `${containerEnginePath} run --rm ${dependencyCheckDatabaseVolume} -v ${elementToScan}:/ms_artifact ${containerImageName}:${toolVersion} sh -c "devsecops-engine-tools --platform_devops local --remote_config_source local --xray_mode ${xrayMode} --remote_config_repo docker_default_remote_config --module engine_dependencies --tool ${dependenciesTool} --token_engine_dependencies ${dependenciesToken} --folder_path /ms_artifact --context true"`;

      const childProcess = exec(containerCommand, (error, stdout, stderr) => {
        clearTimeout(timeout);
        if (error) {
          outputChannel.appendLine(
            `Error executing container command: ${error.message}`
          );
          if (stderr.includes("Unable to find image")) {
            outputChannel.appendLine(
              "Container image not found. Attempting to download..."
            );
          } else {
            outputChannel.appendLine(`Standard Error: ${stderr}`);
            outputChannel.appendLine(
              "Attempting to process partial results..."
            );
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
        outputChannel.appendLine(`Error during dependencies scanning: ${error instanceof Error ? error.message : String(error)}`);
        resolve(new ScannerRes(false, []));
      }
    });
  }

}
