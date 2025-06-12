import { OutputChannel } from "vscode";
import { IDependenciesScanUseCase } from "./interfaces/IDependenciesScanUseCase";
import IScannerGateway from "../model/gateways/IScannerGateway";
import { ScannerRes } from "../model/ScannerRes";
import { ScanConfiguration } from "../model/ScanConfiguration";

export class DependenciesScanUseCase implements IDependenciesScanUseCase {
  constructor(
    private dependenciesScanner: IScannerGateway,
    private dockerImageVersion: string,
    private dockerPath: string
  ) {}

  async scan(
    folderToScan: string,
    outputChannel: OutputChannel,
    scanConfiguration: ScanConfiguration
  ): Promise<ScannerRes> {
    return await this.dependenciesScanner.scan(
      folderToScan,
      outputChannel,
      scanConfiguration.getDockerImageName(),
      this.dockerImageVersion,
      this.dockerPath,
      scanConfiguration.getDependenciesToken(),
      scanConfiguration.getXrayMode(),
      scanConfiguration.getDependenciesTool()
    );
  }
}
