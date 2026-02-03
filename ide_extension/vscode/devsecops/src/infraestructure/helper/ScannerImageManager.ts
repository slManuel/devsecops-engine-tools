import { OutputChannel } from "vscode";
import { exec } from "child_process";
import { promisify } from "util";
import { DockerErrorHandler, ErrorContext } from "./DockerErrorHandler";
import { NetworkErrorHandler } from "./NetworkErrorHandler";
import { DockerValidator } from "./DockerValidator";

const execAsync = promisify(exec);
export class ScannerImageManager {
  private readonly dockerErrorHandler: DockerErrorHandler;
  private readonly networkErrorHandler: NetworkErrorHandler;

  constructor() {
    this.dockerErrorHandler = new DockerErrorHandler();
    this.networkErrorHandler = new NetworkErrorHandler();
  }

  public getLastErrorCategory(): 'critical-docker' | 'docker' | 'network' | null {
    const dockerCategory = this.dockerErrorHandler.getLastErrorCategory();
    if (dockerCategory) {
      return dockerCategory;
    }
    
    if (this.networkErrorHandler.hasNetworkError()) {
      return 'network';
    }
    
    return null;
  }

  async ensureScannerImageExists(
    containerEnginePath: string,
    containerImageName: string,
    toolVersion: string,
    outputChannel: OutputChannel,
    logCapture?: (message: string) => void
  ): Promise<boolean> {
    this.dockerErrorHandler.reset();
    this.networkErrorHandler.reset();

    if (!DockerValidator.isDockerInstalled(containerEnginePath, outputChannel)) {
      if (logCapture) {
        logCapture("Docker is not installed or not accessible");
      }
      return false;
    }

    const imageTag = `${containerImageName}:${toolVersion}`;
    const context: ErrorContext = { imageTag, containerImageName, toolVersion };

    const imageExists = await this.checkImageExists(containerEnginePath, imageTag, outputChannel, logCapture);
    if (imageExists) {
      return true;
    }

    return await this.pullImage(containerEnginePath, imageTag, outputChannel, context, logCapture);
  }

  private async checkImageExists(
    containerEnginePath: string,
    imageTag: string,
    outputChannel: OutputChannel,
    logCapture?: (message: string) => void
  ): Promise<boolean> {
    const checkCommand = `${containerEnginePath} image inspect ${imageTag}`;
    try {
      await execAsync(checkCommand);
      const message = `Scanner image ${imageTag} found locally.`;
      outputChannel.appendLine(message);
      if (logCapture) {
        logCapture(message);
      }
      return true;
    } catch (error: any) {
      this.handleError(error.message, outputChannel, { imageTag }, logCapture);
      if (logCapture) {
        logCapture(error.message);
      }
      return false;
    }
  }

 private async pullImage(
    containerEnginePath: string,
    imageTag: string,
    outputChannel: OutputChannel,
    context: ErrorContext,
    logCapture?: (message: string) => void
  ): Promise<boolean> {
    try {
      const pullCommand = `${containerEnginePath} pull ${imageTag}`;
      const pullProcess = exec(pullCommand);

      this.attachPullProcessListeners(pullProcess, outputChannel, context, logCapture);

      await execAsync(pullCommand);
      outputChannel.appendLine('');
      const successMessage = `Successfully downloaded scanner image ${imageTag}`;
      outputChannel.appendLine(successMessage);
      if (logCapture) {
        logCapture(successMessage);
      }
      return true;
    } catch (pullError: any) {
      this.handleError(pullError.message, outputChannel, context, logCapture);
      if (logCapture) {
        logCapture(pullError.message);
      }
      return false;
    }
  }

  private attachPullProcessListeners(
    pullProcess: ReturnType<typeof exec>,
    outputChannel: OutputChannel,
    context: ErrorContext,
    logCapture?: (message: string) => void
  ): void {
    pullProcess.stdout?.on('data', (data) => {
      const message = data.toString();
      outputChannel.append(message);
      if (logCapture) {
        logCapture(message);
      }
    });

    pullProcess.stderr?.on('data', (data) => {
      const errorStr = data.toString();
      this.handleError(errorStr, outputChannel, context, logCapture);
      if (logCapture) {
        logCapture(errorStr);
      }
    });
  }

  private handleError(errorMessage: string, outputChannel: OutputChannel, context: ErrorContext, logCapture?: (message: string) => void): void {
    const dockerPatterns = DockerErrorHandler.getErrorPatterns();
    const isDockerError = dockerPatterns.some(pattern => errorMessage.includes(pattern));
    
    if (isDockerError) {
      this.dockerErrorHandler.handle(errorMessage, outputChannel, context, logCapture);
      return;
    }
    
    const networkPatterns = NetworkErrorHandler.getErrorPatterns();
    const isNetworkError = networkPatterns.some(pattern => errorMessage.includes(pattern));
    
    if (isNetworkError) {
      this.networkErrorHandler.handle(errorMessage, outputChannel, context, logCapture);
    } else {
      this.dockerErrorHandler.handle(errorMessage, outputChannel, context, logCapture);
    }
  }

  static async ensureScannerImageExists(
    containerEnginePath: string,
    containerImageName: string,
    toolVersion: string,
    outputChannel: OutputChannel,
    logCapture?: (message: string) => void
  ): Promise<boolean> {
    const manager = new ScannerImageManager();
    return manager.ensureScannerImageExists(containerEnginePath, containerImageName, toolVersion, outputChannel, logCapture);
  }
}
