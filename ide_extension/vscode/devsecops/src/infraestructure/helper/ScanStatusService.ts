import { IMetricsData } from "../../domain/model/metrics/IMetricsData";
import { LogAnalysisService } from "./LogAnalysisService";

export class ScanStatusService {
    public static determineScanStatus(
        scanSuccess: boolean,
        findingsCount: number,
        hasLogErrors: boolean,
        logs?: string[]
    ): IMetricsData['scan_status'] {
        if (hasLogErrors || !scanSuccess) {
            if (logs && logs.length > 0) {
                if (LogAnalysisService.hasCriticalDockerErrors(logs)) {
                    return 'Error: Docker inactive';
                }
                if (LogAnalysisService.hasNetworkErrors(logs)) {
                    return 'Error: VPN inactive';
                }
                if (LogAnalysisService.hasDockerErrors(logs)) {
                    return 'Error: Docker inactive';
                }
                if (LogAnalysisService.hasConfigurationErrors(logs)) {
                    return 'Error: Configuration issues';
                }
            }
            return 'Error: Unknown';
        }

        return findingsCount > 0
            ? 'Success with findings'
            : 'Success with no findings';
    }
}