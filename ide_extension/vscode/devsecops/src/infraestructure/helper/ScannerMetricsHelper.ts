import { OutputChannel } from "vscode";
import { Finding } from "../../domain/model/Finding";
import { ISeverityCounts } from "../../domain/model/mappers/Mappers";
import { IMetricsInput } from "../../domain/model/metrics/IMetricsData";
import { MetricsCollectorService } from "./MetricsCollectorService";
import { MetricsStorageService } from "./MetricsStorageService";

/**
 * Helper class for consistent metrics collection across all scanner implementations.
 * Uses composition pattern to avoid code duplication while maintaining consistency.
 */
export class ScannerMetricsHelper {
    private outputLogs: string[] = [];

    /**
     * Clear all captured logs (call at the start of each scan)
     */
    clearLogs(): void {
        this.outputLogs = [];
    }

    /**
     * Get a copy of all captured logs
     */
    getLogs(): string[] {
        return [...this.outputLogs];
    }

    /**
     * Capture a log message to both output channel and internal logs array
     * @param outputChannel VS Code output channel for user visibility
     * @param message Message to log and capture
     */
    captureLog(outputChannel: OutputChannel, message: string): void {
        outputChannel.appendLine(message);
        this.outputLogs.push(message);
    }

    /**
     * Capture a log message without writing to output channel
     * Used when the message has already been written to the channel
     * @param message Message to capture for metrics
     */
    captureOnly(message: string): void {
        this.outputLogs.push(message);
    }

    /**
     * Collect and store structured metrics data from scan results
     * @param elementToScan The element that was scanned (file, directory, image, etc.)
     * @param findings Array of security findings discovered
     * @param severityCounts Severity count breakdown
     * @param scanResult Whether the scan completed successfully
     * @param scanType The type of scan being performed (used as fallback when findings are empty)
     */
    async collectAndstoreMetricsData(
        elementToScan: string,
        findings: Finding[],
        severityCounts: ISeverityCounts | null,
        scanResult: boolean,
        scanType: "engine_iac" | "engine_container" | "engine_dependencies"
    ): Promise<void> {
        try {
            // Prepare metrics input data
            const metricsInput: IMetricsInput = {
                scan_component: elementToScan,
                findings: findings,
                severityCounts: severityCounts,
                scan_success: scanResult,
                output_logs: this.outputLogs,
                exception_message: `Found ${findings.length} issues in scan`,
                tool: scanType
            };

            // Collect structured metrics using the service
            const metricsData = MetricsCollectorService.collectMetrics(metricsInput);

            // Upload metrics to server
            await MetricsStorageService.storeMetricsData(metricsData);

        } catch (error) {
            const errorMessage = `Failed to collect metrics: ${error instanceof Error ? error.message : String(error)}`;
            this.outputLogs.push(errorMessage);
        }
    }

    /**
     * Capture error logs with consistent formatting
     * @param outputChannel VS Code output channel
     * @param error The error that occurred
     * @param context Additional context about where the error occurred
     */
    captureError(outputChannel: OutputChannel, error: unknown, context: string): void {
        const errorMessage = `Error ${context}: ${error instanceof Error ? error.message : String(error)}`;
        this.captureLog(outputChannel, errorMessage);
    }

    /**
     * Capture exit code information with consistent formatting
     * @param outputChannel VS Code output channel
     * @param exitCode The process exit code
     */
    captureExitCode(outputChannel: OutputChannel, exitCode: number): void {
        if (exitCode !== 0) {
            const exitMessage = `Container process exited with code ${exitCode}`;
            this.captureLog(outputChannel, exitMessage);
        }
    }
}