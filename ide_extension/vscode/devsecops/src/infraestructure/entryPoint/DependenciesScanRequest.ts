import { OutputChannel } from "vscode";
import { IDependenciesScanUseCase } from "../../domain/usecase/interfaces/IDependenciesScanUseCase";
import { ScannerRes } from "../../domain/model/ScannerRes";
import { ScanConfiguration } from "../../domain/model/ScanConfiguration";

export class DependenciesScanRequest {
  constructor(private dependenciesScannerUseCase: IDependenciesScanUseCase) {}

  async makeScan(
    folderToScan: string,
    outputChannel: OutputChannel,
    scanConfiguration: ScanConfiguration
  ): Promise<ScannerRes> {
    return await this.dependenciesScannerUseCase.scan(
      folderToScan,
      outputChannel,
      scanConfiguration
    );
  }
}
