import { IMetricsData, IMetricsInput } from "../../domain/model/metrics/IMetricsData";
import { LogAnalysisService } from "./LogAnalysisService";
import { ScanStatusService } from "./ScanStatusService";
import { ToolIdentificationService } from "./ToolIdentificationService";

/**
 * Service responsible for orchestrating the collection and structuring of metrics data.
 * This service coordinates specialized services to create comprehensive scan metrics.
 * 
 * Follows Single Responsibility Principle - only orchestrates, delegates specific tasks to specialized services.
 */
export class MetricsCollectorService {

    /**
     * Collects and structures metrics data from scan results
     * @param input The input data needed to generate metrics
     * @returns Structured metrics data
     */
    public static collectMetrics(input: IMetricsInput): IMetricsData {
        // Delegate to specialized services
        const severityCounts = this.parseSeverityCounts(input.severityCounts);
        const hasLogErrors = LogAnalysisService.hasErrors(input.output_logs);
        const scanStatus = ScanStatusService.determineScanStatus(
            input.scan_success,
            input.findings.length,
            hasLogErrors
        );
        const exceptionLog = LogAnalysisService.extractExceptionMessage(
            input.output_logs,
            input.findings.length,
            input.exception_message
        );
        const tool = ToolIdentificationService.determine(
            input.findings,
            input.tool
        );

        // Orchestrate the final metrics data structure
        const metricsData: IMetricsData = {
            tool: tool,
            scan_component: input.scan_component,
            scan_date: new Date().toLocaleString(),
            findings_severity_critical: severityCounts.critical,
            findings_severity_high: severityCounts.high,
            findings_severity_medium: severityCounts.medium,
            findings_severity_low: severityCounts.low,
            total_findings: input.findings.length.toString(),
            exception_log: exceptionLog,
            scan_status: scanStatus
        };

        return metricsData;
    }

    /**
     * Parse and normalize severity counts from scanner output
     * Simple data transformation - no business logic
     */
    private static parseSeverityCounts(severityCounts: IMetricsInput['severityCounts']) {
        if (!severityCounts) {
            return { critical: "0", high: "0", medium: "0", low: "0" };
        }

        return {
            critical: severityCounts.critical || "0",
            high: severityCounts.high || "0",
            medium: severityCounts.medium || "0",
            low: severityCounts.low || "0"
        };
    }
}