import { OutputChannel } from "vscode";
import { IDependenciesScanUseCase } from "./interfaces/IDependenciesScanUseCase";
import IScannerGateway from "../model/gateways/IScannerGateway";
import { ScannerRes } from "../model/ScannerRes";
import { ScanConfiguration } from "../model/ScanConfiguration";

export class DependenciesScanUseCase implements IDependenciesScanUseCase {
  constructor(
    private dependenciesScanner: IScannerGateway,
    private containerImageVersion: string,
    private containerEnginePath: string
  ) {}

  async scan(
    folderToScan: string,
    outputChannel: OutputChannel,
    scanConfiguration: ScanConfiguration
  ): Promise<ScannerRes> {
    return await this.dependenciesScanner.scan(
      folderToScan,
      outputChannel,
      scanConfiguration.getContainerImageName(),
      this.containerImageVersion,
      this.containerEnginePath,
      scanConfiguration.getDependenciesToken(),
      scanConfiguration.getXrayMode(),
      scanConfiguration.getDependenciesTool(),
      scanConfiguration.getDependencyCheckDatabase()
    );
  }
}
