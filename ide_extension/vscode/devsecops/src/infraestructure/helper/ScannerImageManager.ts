import { OutputChannel } from "vscode";
import { exec } from "child_process";
import { promisify } from "util";
import { DockerErrorHandler, ErrorContext } from "./DockerErrorHandler";
import { DockerValidator } from "./DockerValidator";

const execAsync = promisify(exec);
export class ScannerImageManager {
  private readonly errorHandler: DockerErrorHandler;

  constructor() {
    this.errorHandler = new DockerErrorHandler();
  }

  async ensureScannerImageExists(
    containerEnginePath: string,
    containerImageName: string,
    toolVersion: string,
    outputChannel: OutputChannel
  ): Promise<boolean> {
    if (!DockerValidator.isDockerInstalled(containerEnginePath, outputChannel)) {
      return false;
    }

    const imageTag = `${containerImageName}:${toolVersion}`;
    const context: ErrorContext = { imageTag, containerImageName, toolVersion };

    const imageExists = await this.checkImageExists(containerEnginePath, imageTag, outputChannel);
    if (imageExists) {
      return true;
    }

    this.errorHandler.reset();
    return await this.pullImage(containerEnginePath, imageTag, outputChannel, context);
  }

  private async checkImageExists(
    containerEnginePath: string,
    imageTag: string,
    outputChannel: OutputChannel
  ): Promise<boolean> {
    const checkCommand = `${containerEnginePath} image inspect ${imageTag}`;
    try {
      await execAsync(checkCommand);
      outputChannel.appendLine(`Scanner image ${imageTag} found locally.`);
      return true;
    } catch (error: any) {
      this.errorHandler.handle(error.message, outputChannel, { imageTag });
      return false;
    }
  }

  private async pullImage(
    containerEnginePath: string,
    imageTag: string,
    outputChannel: OutputChannel,
    context: ErrorContext
  ): Promise<boolean> {
    try {
      const pullCommand = `${containerEnginePath} pull ${imageTag}`;
      const pullProcess = exec(pullCommand);

      this.attachPullProcessListeners(pullProcess, outputChannel, context);

      await execAsync(pullCommand);
      outputChannel.appendLine('');
      outputChannel.appendLine(`Successfully downloaded scanner image ${imageTag}`);
      return true;
    } catch (pullError: any) {
      this.errorHandler.handle(pullError.message, outputChannel, context);
      return false;
    }
  }

  private attachPullProcessListeners(
    pullProcess: ReturnType<typeof exec>,
    outputChannel: OutputChannel,
    context: ErrorContext
  ): void {
    pullProcess.stdout?.on('data', (data) => {
      outputChannel.append(data.toString());
    });

    pullProcess.stderr?.on('data', (data) => {
      const errorStr = data.toString();
      if (this.isNetworkError(errorStr)) {
        this.errorHandler.handle(errorStr, outputChannel, context);
      } else {
        outputChannel.append(errorStr);
      }
    });
  }

  private isNetworkError(errorMessage: string): boolean {
    return errorMessage.includes('i/o timeout') || errorMessage.includes('Error response from daemon: Get');
  }

  // Static method for backward compatibility
  static async ensureScannerImageExists(
    containerEnginePath: string,
    containerImageName: string,
    toolVersion: string,
    outputChannel: OutputChannel
  ): Promise<boolean> {
    const manager = new ScannerImageManager();
    return manager.ensureScannerImageExists(containerEnginePath, containerImageName, toolVersion, outputChannel);
  }
}
