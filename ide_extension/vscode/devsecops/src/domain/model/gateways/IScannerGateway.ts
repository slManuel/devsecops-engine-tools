import { OutputChannel } from "vscode";
import { ScannerRes } from "../ScannerRes";

export default interface IScannerGateway {
  scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    dockerImageName: string,
    toolVersion?: string,
    dockerPath?: string,
    dependenciesToken?: string,
    xrayMode?: string,
    dependenciesTool?: string
  ): Promise<ScannerRes>;
}
