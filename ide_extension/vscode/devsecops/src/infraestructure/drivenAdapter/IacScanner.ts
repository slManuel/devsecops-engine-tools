import { OutputChannel } from "vscode";
import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import OutputManager from "../helper/OutputManager";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { Finding } from "../../domain/model/Finding";

import { exec, execSync } from "child_process";
import { IIacContext, Mappers } from "../../domain/model/mappers/Mappers";

export class IacScanner implements IScannerGateway {
  async scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    dockerImageName: string,
    toolVersion: string,
    dockerPath: string
  ): Promise<ScannerRes> {
    outputChannel.clear();
    outputChannel.show();
    return new Promise((resolve, _reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];

      const timeout = setTimeout(() => {
        outputChannel.appendLine("Scan timed out after 2 minutes");
        outputChannel.appendLine("Docker command may be hanging. Check Docker configuration.");
        resolve(new ScannerRes(false, []));
      }, 120000);

      const dockerCommand = `${dockerPath} run --rm -v ${elementToScan}:/ms_artifact ${dockerImageName}:${toolVersion} sh -c "devsecops-engine-tools --platform_devops local --remote_config_source local --remote_config_repo docker_default_remote_config --module engine_iac --tool checkov --folder_path /ms_artifact --context true"`;

      const childProcess = exec(dockerCommand, (error, stdout, stderr) => {
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
          outputChannel.appendLine(`Found ${findings.length} issues in scan`);
        } else {
          outputChannel.appendLine("Docker command completed with no output");
        }

        resolve(new ScannerRes(scanResult, findings));
      });

      childProcess.on("exit", (code) => {
        if (code !== 0 && code !== null) {
          outputChannel.appendLine(`Docker process exited with code ${code}`);
        }
      });
    });
  }

  getRuleCode(
    dockerPath: string,
    dockerImageName: string,
    toolVersion: string,
    ruleId: string,
    finding: Finding
  ): Finding {
    const dockerCommand = `${dockerPath} run --rm ${dockerImageName}:${toolVersion}  python3 rules_context_extract.py ${ruleId}`;
    const rulePrint = execSync(dockerCommand, { encoding: "utf-8" }).trim();
    finding.setValidationRuleCode(rulePrint);
    return finding;
  }

  private errorHandler(outputChannel: OutputChannel, error: Error, stderr: string): void {
    outputChannel.appendLine(`Error: ${error.message}`);
    outputChannel.appendLine("Please check your Docker configuration and try again.");
    if (stderr.includes("Unable to find image")) {
      outputChannel.appendLine("Docker image not found. Attempting to download...");
    } else {
      outputChannel.appendLine(`Standard Error: ${stderr}`);
      outputChannel.appendLine("Attempting to process partial results...");
    }
  }
}
