import { OutputChannel } from "vscode";
import { Finding } from "../../domain/model/Finding";
import { ISeverityCounts } from "../../domain/model/mappers/Mappers";
import { IMetricsInput } from "../../domain/model/metrics/IMetricsData";
import { MetricsCollectorService } from "./MetricsCollectorService";
import { MetricsStorageService } from "./MetricsStorageService";

export class ScannerMetricsHelper {
    private outputLogs: string[] = [];

    clearLogs(): void {
        this.outputLogs = [];
    }

    getLogs(): string[] {
        return [...this.outputLogs];
    }

    captureLog(outputChannel: OutputChannel, message: string): void {
        outputChannel.appendLine(message);
        this.outputLogs.push(message);
    }

    captureOnly(message: string): void {
        this.outputLogs.push(message);
    }

    async collectAndstoreMetricsData(
        elementToScan: string,
        findings: Finding[],
        severityCounts: ISeverityCounts | null,
        scanResult: boolean,
        scanType: "engine_iac" | "engine_container" | "engine_dependencies"
    ): Promise<void> {
        try {
            const metricsInput: IMetricsInput = {
                scan_component: elementToScan,
                findings: findings,
                severityCounts: severityCounts,
                scan_success: scanResult,
                output_logs: this.outputLogs,
                exception_message: `Found ${findings.length} issues in scan`,
                tool: scanType
            };

            const metricsData = MetricsCollectorService.collectMetrics(metricsInput);

            await MetricsStorageService.storeMetricsData(metricsData);

        } catch (error) {
            const errorMessage = `Failed to collect metrics: ${error instanceof Error ? error.message : String(error)}`;
            this.outputLogs.push(errorMessage);
        }
    }

    captureError(outputChannel: OutputChannel, error: unknown, context: string): void {
        const errorMessage = `Error ${context}: ${error instanceof Error ? error.message : String(error)}`;
        this.captureLog(outputChannel, errorMessage);
    }

    captureExitCode(outputChannel: OutputChannel, exitCode: number): void {
        if (exitCode !== 0) {
            const exitMessage = `Container process exited with code ${exitCode}`;
            this.captureLog(outputChannel, exitMessage);
        }
    }
}