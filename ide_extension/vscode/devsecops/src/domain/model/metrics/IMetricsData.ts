
export interface IMetricsData {
    tool: string;
    scan_component: string;
    scan_date: string;
    findings_severity_critical: string;
    findings_severity_high: string;
    findings_severity_medium: string;
    findings_severity_low: string;
    total_findings: string;
    exception_log: string;
    scan_status: 'Success with findings' | 'Success with no findings' | 'Error';
}

export interface IMetricsInput {
    tool?: string;
    scan_component: string;
    findings: any[];
    severityCounts: {
        critical: string;
        high: string;
        medium: string;
        low: string;
    } | null;
    scan_success: boolean;
    output_logs: string[];
    exception_message?: string;
}
