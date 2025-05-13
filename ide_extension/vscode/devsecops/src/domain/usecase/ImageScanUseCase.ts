import { OutputChannel } from "vscode";
import { IImageScanUseCase } from "./interfaces/IImageScanUseCase";
import IScannerGateway from "../model/gateways/IScannerGateway";
import { ScannerRes } from "../model/ScannerRes";

export class ImageScanUseCase implements IImageScanUseCase {
  constructor(
    private imageScanner: IScannerGateway,
    private dockerImageVersion: string,
    private dockerPath: string
  ) {}

  async scan(
    imageToScan: string,
    outputChannel: OutputChannel,
    dockerImageName: string
  ): Promise<ScannerRes> {
    return await this.imageScanner.scan(
      imageToScan,
      outputChannel,
      dockerImageName,
      this.dockerImageVersion,
      this.dockerPath
    );
  }
}
