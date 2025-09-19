/**
 * Interface representing the structured metrics data collected from scanning processes
 */
export interface IMetricsData {
    /** The scanning tool/practice used: engine_iac | engine_container | engine_dependencies */
    tool: string;

    /** The component being scanned (full path to project or image name) */
    scan_component: string;

    /**Timestamp when the scan was performed */
    scan_date: string;

    /** Number of critical severity findings */
    findings_severity_critical: string;

    /** Number of high severity findings */
    findings_severity_high: string;

    /** Number of medium severity findings */
    findings_severity_medium: string;

    /** Number of low severity findings */
    findings_severity_low: string;

    /** Total number of findings across all severities */
    total_findings: string;

    /** Exception or summary log message from the scan */
    exception_log: string;

    /** Status of the scan: Success with findings | success_no_findings | error */
    scan_status: 'Success with findings' | 'Success with no findings' | 'Error';
}

/**
 * Input data needed to generate metrics
 */
export interface IMetricsInput {
    /** The scanning tool/practice identifier (optional, will be determined from findings if not provided) */
    tool?: string;

    /** The component being scanned */
    scan_component: string;

    /** Array of findings from the scan */
    findings: any[];

    /** Severity counts object */
    severityCounts: {
        critical: string;
        high: string;
        medium: string;
        low: string;
    } | null;

    /** Whether the scan was successful */
    scan_success: boolean;

    /** Output channel logs (for error detection) */
    output_logs: string[];

    /** Additional context or error messages */
    exception_message?: string;
}