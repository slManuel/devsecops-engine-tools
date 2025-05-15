import { OutputChannel } from "vscode";
import { ScannerRes } from "../../model/ScannerRes";

export interface IImageScanUseCase {
  scan(
    imageToScan: string,
    outputChannel: OutputChannel,
    dockerImageName: string
  ): Promise<ScannerRes>;
}
