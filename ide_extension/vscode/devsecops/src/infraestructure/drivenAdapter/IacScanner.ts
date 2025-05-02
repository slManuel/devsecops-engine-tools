import { OutputChannel } from "vscode";
import IScannerGateway from "../../domain/model/gateways/IScannerGateway";
import {exec} from 'child_process';
import OutputManager from "../helper/OutputManager";

export class IacScanner implements IScannerGateway{

    async scan(elementToScan: string, outputChannel: OutputChannel, toolVersion: string): Promise<boolean> {
        let scanResult: boolean = false;
        // exec(`/usr/local/bin/docker run --rm -v ${elementToScan}:/ms_artifact artifactory.apps.bancolombia.com/devops/devsecops-engine-tools:${toolVersion}  devsecops-engine-tools --platform_devops local --remote_config_repo docker_default_remote_config --module engine_iac --tool checkov --folder_path /ms_artifact`, (error, stdout, stderr) => {
        exec(`/usr/local/bin/docker run --rm -v ${elementToScan}:/ms_artifact bancolombia/devsecops-engine-tools:${toolVersion}  devsecops-engine-tools --platform_devops local --remote_config_repo docker_default_remote_config --module engine_iac --tool checkov --folder_path /ms_artifact`, (error, stdout, stderr) => {
            if (error) {
                if (stderr.includes('Unable to find image')) {
                    console.log('Docker image not found. Downloading the image');
                    exec(`docker pull artifactory.apps.bancolombia.com/devops/devsecops-engine-tools:${toolVersion}`, (error, stdout, stderr) => {
                        if (error) {
                            console.error(`exec error: ${error}`);
                            console.error(`stderr: ${stderr}`);
                            outputChannel.appendLine(`Failed to download Docker image: ${error.message}`);
                            outputChannel.appendLine('Error: Unable to download the specified Docker image.');
                            outputChannel.appendLine('Please check if the image exists in the registry or if you have the correct permissions.');
                            outputChannel.appendLine('Contact your DevSecOps team for assistance with the correct image version.');
                        }
                        outputChannel.appendLine('Docker image downloaded successfully');
                        this.scan(elementToScan, outputChannel, toolVersion);
                    });
                }
                console.error(`exec error: ${error}`);
                console.error(`stderr: ${stderr}`);
            }

            const cleanedOutput = OutputManager.removeAnsiEscapeCodes(stdout);
            outputChannel.appendLine(cleanedOutput);
            outputChannel.show();
            scanResult = true;
        });
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(scanResult);
            }, 10000);
        });
    }

}