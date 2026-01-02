import { IMetricsData } from "../../domain/model/metrics/IMetricsData";
import { LogAnalysisService } from "./LogAnalysisService";

export class ScanStatusService {
    /**
     * Determines the scan status based on scan results and log analysis.
     * 
     * @param scanSuccess - Whether the scan completed without errors
     * @param findingsCount - Number of security findings discovered
     * @param hasLogErrors - Whether error patterns were detected in logs
     * @param logs - Optional array of log messages for error categorization
     * @returns Categorized scan status for metrics
     */
    public static determineScanStatus(
        scanSuccess: boolean,
        findingsCount: number,
        hasLogErrors: boolean,
        logs?: string[]
    ): IMetricsData['scan_status'] {
        // If scan failed or errors were detected in logs
        if (hasLogErrors || !scanSuccess) {
            // Categorize the specific type of error by analyzing logs
            if (logs && logs.length > 0) {
                // Check in priority order: Docker > Network > Configuration
                if (LogAnalysisService.hasDockerErrors(logs)) {
                    return 'Docker Error';
                }
                if (LogAnalysisService.hasNetworkErrors(logs)) {
                    return 'Network Error';
                }
                if (LogAnalysisService.hasConfigurationErrors(logs)) {
                    return 'Configuration Error';
                }
            }
            // Fallback for errors that don't match specific patterns
            return 'Unknown Error';
        }

        // Scan succeeded - differentiate between findings vs no findings
        return findingsCount > 0
            ? 'Success with findings'
            : 'Success with no findings';
    }
}