import { OutputChannel } from "vscode";
import { IImageScanUseCase } from "../../domain/usecase/interfaces/IImageScanUseCase";
import { ScannerRes } from "../../domain/model/ScannerRes";

export class ImageScanRequest {

    constructor(private imageScanUseCase: IImageScanUseCase){}

    makeScan(elementToScan: string, outputChannel: OutputChannel, dockerImageName: string): Promise<ScannerRes> {
        return this.imageScanUseCase.scan(
            elementToScan,
            outputChannel,
            dockerImageName
        );
    }

}