import { OutputChannel } from "vscode";
import { ScannerRes } from "../ScannerRes";

export default interface IScannerGateway {
  scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    containerImageName: string,
    toolVersion?: string,
    containerEnginePath?: string,
    dependenciesToken?: string,
    xrayMode?: string,
    dependenciesTool?: string,
    dependencyCheckDatabase?: string
  ): Promise<ScannerRes>;
}
