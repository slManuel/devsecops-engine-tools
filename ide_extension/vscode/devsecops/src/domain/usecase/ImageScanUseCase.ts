import { OutputChannel } from "vscode";
import { IImageScanUseCase } from "./interfaces/IImageScanUseCase";
import IScannerGateway from "../model/gateways/IScannerGateway";

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
  ): Promise<boolean> {
    return await this.imageScanner.scan(
      imageToScan,
      outputChannel,
      dockerImageName,
      this.dockerImageVersion,
      this.dockerPath
    );
  }
}
