import { IMetricsData } from "../../domain/model/metrics/IMetricsData";

/**
 * Service responsible for determining scan status based on business rules.
 * Handles the logic for classifying scans as successful, failed, or with findings.
 */
export class ScanStatusService {

    /**
     * Determine the overall status of a scan based on multiple factors
     * @param scanSuccess Technical success flag from the scanner
     * @param findingsCount Number of findings discovered
     * @param hasLogErrors Whether error indicators were found in logs
     * @returns Scan status classification
     */
    public static determineScanStatus(
        scanSuccess: boolean,
        findingsCount: number,
        hasLogErrors: boolean
    ): IMetricsData['scan_status'] {

        // Priority 1: Check for errors (technical failures)
        if (hasLogErrors || !scanSuccess) {
            return 'Error';
        }

        // Priority 2: Successful scan - classify by findings
        return findingsCount > 0
            ? 'Success with findings'
            : 'Success with no findings';
    }


}