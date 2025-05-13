import { OutputChannel } from "vscode";
import { IImageScanUseCase } from "../../domain/usecase/interfaces/IImageScanUseCase";

export class ImageScanRequest {

    constructor(private imageScanUseCase: IImageScanUseCase){}

    makeScan(elementToScan: string, outputChannel: OutputChannel, dockerImageName: string): Promise<boolean> {
        return this.imageScanUseCase.scan(
            elementToScan,
            outputChannel,
            dockerImageName
        );
    }

}