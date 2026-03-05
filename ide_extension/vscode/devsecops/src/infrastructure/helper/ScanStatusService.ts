import { IMetricsData } from "../../domain/model/metrics/IMetricsData";
import { ErrorHandlingService } from "../services/ErrorHandlingService";

export class ScanStatusService {
    public static determineScanStatus(
        scanSuccess: boolean,
        findingsCount: number,
        hasLogErrors: boolean,
        logs?: string[]
    ): IMetricsData['scan_status'] {
        if (hasLogErrors || !scanSuccess) {
            if (logs && logs.length > 0) {
                if (ErrorHandlingService.hasCriticalDockerErrors(logs)) {
                    return 'Error: Docker inactive';
                }
                if (ErrorHandlingService.hasNetworkErrors(logs)) {
                    return 'Error: VPN inactive';
                }
                if (ErrorHandlingService.hasDockerErrors(logs)) {
                    return 'Error: Docker inactive';
                }
                if (ErrorHandlingService.hasConfigurationErrors(logs)) {
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