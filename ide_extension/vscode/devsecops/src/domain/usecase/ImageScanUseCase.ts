import { OutputChannel } from "vscode";
import { IImageScanUseCase } from "./interfaces/IImageScanUseCase";
import IScannerGateway from "../model/gateways/IScannerGateway";

export class ImageScanUseCase implements IImageScanUseCase {

    constructor(
        private imageScanner: IScannerGateway,
        private dockerImageVersion: string
    ){}
    
    async scan(imageToScan: string, outputChannel: OutputChannel): Promise<boolean> {
        return await this.imageScanner.scan(imageToScan, outputChannel, this.dockerImageVersion);
    }
    
}