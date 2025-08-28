import { OutputChannel } from "vscode";
import { ScannerRes } from "../../model/ScannerRes";
import { ScanConfiguration } from "../../model/ScanConfiguration";

export interface IDependenciesScanUseCase {
  scan(
    imageToScan: string,
    outputChannel: OutputChannel,
    scanConfiguration: ScanConfiguration,
    scanLoader: any
  ): Promise<ScannerRes>;
}
