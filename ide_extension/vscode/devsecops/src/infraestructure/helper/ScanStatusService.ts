import { IMetricsData } from "../../domain/model/metrics/IMetricsData";

export class ScanStatusService {
    public static determineScanStatus(
        scanSuccess: boolean,
        findingsCount: number,
        hasLogErrors: boolean
    ): IMetricsData['scan_status'] {
        if (hasLogErrors || !scanSuccess) {
            return 'Error';
        }
        return findingsCount > 0
            ? 'Success with findings'
            : 'Success with no findings';
    }
}