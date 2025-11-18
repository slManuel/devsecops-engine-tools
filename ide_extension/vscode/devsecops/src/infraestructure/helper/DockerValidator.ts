import { OutputChannel } from "vscode";
import { execSync } from "child_process";

export class DockerValidator {
    static isDockerInstalled(containerEnginePath: string, outputChannel: OutputChannel): boolean {
        try {
            execSync(`${containerEnginePath} --version`, { stdio: 'ignore' });
            return true;
        } catch (err) {
            outputChannel.appendLine('❌ Docker is not installed or not found in the PATH. Please install Docker to continue.');
            return false;
        }
    }
}
