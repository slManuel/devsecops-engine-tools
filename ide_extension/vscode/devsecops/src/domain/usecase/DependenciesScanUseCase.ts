import { OutputChannel } from "vscode";
import { IDependenciesScanUseCase } from "./interfaces/IDependenciesScanUseCase";
import IScannerGateway from "../model/gateways/IScannerGateway";
import { ScannerRes } from "../model/ScannerRes";
import { ScanConfiguration } from "../model/ScanConfiguration";
import { ScanExecutionOrchestrator } from "../../infrastructure/executors/ScanExecutionOrchestrator";
import { IScanExecutionConfig } from "../../infrastructure/executors/IScanExecutor";
import { ScanContextMapper } from "../../infrastructure/mappers/ScanContextMapper";
import { MetricsService } from "../../infrastructure/services/MetricsService";

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
      
      // Create MetricsService instance to capture logs during remote execution
      const metricsService = new MetricsService();
      metricsService.clearLogs();
      
      try {
        // Build config for remote execution
        const scanConfig: IScanExecutionConfig = {
          scanType: 'dependencies',
          target: folderToScan,
          containerImageName: scanConfiguration.getContainerImageName(),
          engineToolsVersion: this.containerImageVersion,
          containerEnginePath: this.containerEnginePath,
          dependenciesTool: scanConfiguration.getDependenciesTool(),
          dependenciesToken: scanConfiguration.getDependenciesToken(),
          xrayMode: scanConfiguration.getXrayMode(),
          dependencyCheckDatabase: scanConfiguration.getDependencyCheckDatabase()
        };

        // Execute via remote microservice with log capture
        const logCapture = (message: string) => metricsService.captureOnly(message);
        const result = await executor.execute(scanConfig, outputChannel, logCapture);

        if (!result.success || !result.contextJson) {
          throw new Error(result.error || 'Remote scan failed');
        }

        // Parse context JSON and map to findings using centralized mapper
        const mappedResult = ScanContextMapper.parseAndMapContext(result.contextJson, 'dependencies');
        
        if (!mappedResult.success) {
          throw new Error(mappedResult.errorMessage || 'Failed to parse scan results');
        }

        // Send metrics for remote execution (non-blocking)
        try {
          await metricsService.collectAndstoreMetricsData(
            folderToScan,
            mappedResult.findings,
            mappedResult.severityCounts,
            mappedResult.success,
            'engine_dependencies'
          );
        } catch (metricsError) {
          // Log but don't fail the scan if metrics upload fails
          console.error('Failed to send metrics:', metricsError);
        }

        return new ScannerRes(mappedResult.success, mappedResult.findings, mappedResult.severityCounts);
      } catch (error) {
        // Send metrics for failed scan before throwing error
        metricsService.captureError(outputChannel, error, 'remote scan execution');
        await metricsService.collectFailedScanMetrics(folderToScan, 'engine_dependencies');
        throw error;
      }
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
