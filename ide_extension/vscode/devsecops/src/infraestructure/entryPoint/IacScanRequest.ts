import { OutputChannel } from "vscode";
import { IIacScanUseCase } from "../../domain/usecase/interfaces/IIacScanUseCase";

export class IacScanRequest {
  constructor(private iacScannerUseCase: IIacScanUseCase) {}

  async makeScan(
    folderToScan: string,
    dockerImageName: string,
    organizationName: string,
    projectName: string,
    groupName: string,
    adUserName: string,
    adPersonalAccessToken: string,
    environment: string,
    outputChannel: OutputChannel
  ): Promise<boolean> {
    return await this.iacScannerUseCase.scan(
      folderToScan,
      dockerImageName,
      organizationName,
      projectName,
      groupName,
      adUserName,
      adPersonalAccessToken,
      environment,
      outputChannel
    );
  }
}
