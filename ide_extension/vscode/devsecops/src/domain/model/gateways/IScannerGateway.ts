import { OutputChannel } from "vscode";

export default interface IScannerGateway {
  scan(
    elementToScan: string,
    outputChannel: OutputChannel,
    dockerImageName: string,
    toolVersion?: string
  ): Promise<boolean>;
}
