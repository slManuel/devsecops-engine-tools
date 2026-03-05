import { OutputChannel } from "vscode";
import { IDependenciesScanUseCase } from "./interfaces/IDependenciesScanUseCase";
import IScannerGateway from "../model/gateways/IScannerGateway";
import { ScannerRes } from "../model/ScannerRes";
import { ScanConfiguration } from "../model/ScanConfiguration";
import { ScanExecutionOrchestrator } from "../../infrastructure/executors/ScanExecutionOrchestrator";
import { IScanExecutionConfig } from "../../infrastructure/executors/IScanExecutor";
import { Mappers } from "../model/mappers/Mappers";

export class DependenciesScanUseCase implements IDependenciesScanUseCase {
  constructor(
    private dependenciesScanner: IScannerGateway,
    private containerImageVersion: string,
    private containerEnginePath: string
  ) { }

  async scan(
    folderToScan: string,
    outputChannel: OutputChannel,
    scanConfiguration: ScanConfiguration,
    scanLoader: any
  ): Promise<ScannerRes> {
    // Select executor based on configuration
    const executor = await ScanExecutionOrchestrator.selectExecutor();
    await ScanExecutionOrchestrator.getExecutionModeStatus(outputChannel);

    // Check if we should use remote executor
    if (executor.getExecutionMode() === 'remote-microservice') {
      // Show output channel
      outputChannel.show();
      
      // Build config for remote execution
      const scanConfig: IScanExecutionConfig = {
        scanType: 'dependencies',
        target: folderToScan,
        containerImageName: scanConfiguration.getContainerImageName(),
        toolVersion: this.containerImageVersion,
        containerEnginePath: this.containerEnginePath,
        dependenciesTool: scanConfiguration.getDependenciesTool(),
        dependenciesToken: scanConfiguration.getDependenciesToken(),
        xrayMode: scanConfiguration.getXrayMode(),
        dependencyCheckDatabase: scanConfiguration.getDependencyCheckDatabase()
      };

      // Execute via remote microservice
      const result = await executor.execute(scanConfig, outputChannel);

      if (!result.success || !result.contextJson) {
        throw new Error(result.error || 'Remote scan failed');
      }

      // Parse context JSON and map to findings
      const contextData = JSON.parse(result.contextJson);
      const findings = (contextData.dependencies_context || []).map((ctx: any) => 
        Mappers.mapDependenciesScanContextToFinding(ctx)
      );

      return new ScannerRes(result.success, findings);
    }

    // Use local Docker execution (traditional flow)
    return await this.dependenciesScanner.scan(
      folderToScan,
      outputChannel,
      scanConfiguration.getContainerImageName(),
      this.containerImageVersion,
      this.containerEnginePath,
      scanConfiguration.getDependenciesToken(),
      scanConfiguration.getXrayMode(),
      scanConfiguration.getDependenciesTool(),
      scanConfiguration.getDependencyCheckDatabase(),
      scanLoader
    );
  }
}
