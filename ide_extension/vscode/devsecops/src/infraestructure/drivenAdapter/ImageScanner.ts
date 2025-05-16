import { OutputChannel } from "vscode";
import OutputManager from "../helper/OutputManager";
import { exec } from "child_process";

import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import { Finding } from "../../domain/model/Finding";
import { ScannerRes } from "../../domain/model/ScannerRes";

export class ImageScanner implements IScannerGateway {
  scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    dockerImageName: string,
    toolVersion: string,
    dockerPath: string
  ): Promise<ScannerRes> {

    outputChannel.clear();
    outputChannel.show();
    
    return new Promise((resolve, reject) => {
      let scanResult: boolean = false;
      let findings: Finding[] = [];
      
      const timeout = setTimeout(() => {
        outputChannel.appendLine("Scan timed out after 2 minutes");
        outputChannel.appendLine("Docker command may be hanging. Check Docker configuration.");
        resolve(new ScannerRes(false, []));
      }, 120000);
          
      const dockerCommand = `${dockerPath} run --rm -v /var/run/docker.sock:/var/run/docker.sock ${dockerImageName}:1.59.0 devsecops-engine-tools --platform_devops local --remote_config_repo docker_default_remote_config --module engine_container --tool trivy --image_to_scan ${elementToScan} --context true`;
      
      const childProcess = exec(
        dockerCommand,
        (error, stdout, stderr) => {
          clearTimeout(timeout);
          if (error) {
            outputChannel.appendLine(`Error executing Docker command: ${error.message}`);
            if (stderr.includes("Unable to find image")) {
              outputChannel.appendLine("Docker image not found. Attempting to download...");
            } else {
              outputChannel.appendLine(`Standard Error: ${stderr}`);
            }
          }
  
          if (stdout) {
            let contextJson = null;
            let normalOutput = stdout;
            
            const contextRegex = /===== BEGIN CONTEXT OUTPUT =====\s*([\s\S]*?)\s*===== END CONTEXT OUTPUT =====/;
            const match = stdout.match(contextRegex);
            
            if (match && match[1]) {
              try {
                contextJson = JSON.parse(match[1].trim());
                
                normalOutput = stdout.replace(contextRegex, "");
                
                findings = contextJson.container_context.map((finding: any) => {
                  return new Finding(
                    finding.id || finding.cve_id || "",
                    finding.custom_vuln_id || finding.id || finding.cve_id || "",
                    finding.check_name || "",
                    finding.check_class || "",
                    finding.severity || "unknown",
                    finding.package_name + " " + finding.os_type + ":" + finding.layer_digest || "",
                    finding.resource || "",
                    finding.description || "",
                    finding.module || "engine_container",
                    finding.source_tool || "Trivy",
                    finding.references || []
                  );
                });
                
                scanResult = true;
                outputChannel.appendLine(`Successfully extracted context data with ${findings.length} findings`);
              } catch (jsonError) {
                outputChannel.appendLine(`Error parsing context JSON: ${jsonError}`);
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
            outputChannel.appendLine("Docker command completed with no output");
          }
          
          resolve(new ScannerRes(scanResult, findings));
        }
      );
      
      childProcess.on('exit', (code) => {
        if (code !== 0 && code !== null) {
          outputChannel.appendLine(`Docker process exited with code ${code}`);
        }
      });
    });
  }
}
