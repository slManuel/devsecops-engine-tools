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
            // Priority: Critical Docker (daemon issues) > Network/VPN > Other Docker > Configuration
            if (logs && logs.length > 0) {
                // Check critical Docker errors first (daemon not running, Docker not accessible)
                if (LogAnalysisService.hasCriticalDockerErrors(logs)) {
                    return 'Error: Docker inactive';
                }
                // Then check network/VPN errors
                if (LogAnalysisService.hasNetworkErrors(logs)) {
                    return 'Error: VPN inactive';
                }
                // Then check other Docker errors (invalid commands, permissions, etc.)
                if (LogAnalysisService.hasDockerErrors(logs)) {
                    return 'Error: Docker inactive';
                }
                // Finally check configuration errors
                if (LogAnalysisService.hasConfigurationErrors(logs)) {
                    return 'Error: Configuration issues';
                }
            }
            // Fallback for errors that don't match specific patterns
            return 'Error: Unknown';
        }

        // Scan succeeded - differentiate between findings vs no findings
        return findingsCount > 0
            ? 'Success with findings'
            : 'Success with no findings';
    }
}