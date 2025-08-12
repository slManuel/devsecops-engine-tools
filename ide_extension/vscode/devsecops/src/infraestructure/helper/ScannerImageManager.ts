import { OutputChannel } from "vscode";
import { exec } from "child_process";

export class ScannerImageManager {
  static async ensureScannerImageExists(
    containerEnginePath: string,
    containerImageName: string,
    toolVersion: string,
    outputChannel: OutputChannel
  ): Promise<boolean> {
    const imageTag = `${containerImageName}:${toolVersion}`;
    
    return new Promise((resolve) => {
      const checkCommand = `${containerEnginePath} image inspect ${imageTag}`;
      
      exec(checkCommand, (error, stdout, stderr) => {
        if (!error) {
          outputChannel.appendLine(`Scanner image ${imageTag} found locally`);
          resolve(true);
          return;
        }
        
        outputChannel.appendLine(`Scanner image ${imageTag} not found locally, downloading...`);
        
        const pullCommand = `${containerEnginePath} pull ${imageTag}`;
        const pullProcess = exec(pullCommand, (pullError, pullStdout, pullStderr) => {
          if (pullError) {
            outputChannel.appendLine(`Failed to download scanner image: ${pullError.message}`);
            if (pullStderr) {
              outputChannel.appendLine(`Pull stderr: ${pullStderr}`);
            }
            resolve(false);
            return;
          }
          
          outputChannel.appendLine(`Successfully downloaded scanner image ${imageTag}`);
          resolve(true);
        });

        pullProcess.stdout?.on('data', (data) => {
          outputChannel.append(data.toString());
        });
        
        pullProcess.stderr?.on('data', (data) => {
          outputChannel.append(data.toString());
        });
      });
    });
  }
}
