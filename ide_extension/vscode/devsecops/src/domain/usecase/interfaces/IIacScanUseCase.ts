import { OutputChannel } from "vscode";
import { ScannerRes } from "../../model/ScannerRes";

export interface IIacScanUseCase {
    scan(folderToScan: string,
        dockerImageName: string,
        organizationName: string,
        projectName: string,
        definitionId: string,
        adUserName: string,
        adPersonalAccessToken: string,
        environment: string,
        outputChannel: OutputChannel
    ): Promise<ScannerRes>;
}