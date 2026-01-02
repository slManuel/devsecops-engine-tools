import { IMetricsData, IMetricsInput } from "../../domain/model/metrics/IMetricsData";
import { LogAnalysisService } from "./LogAnalysisService";
import { ScanStatusService } from "./ScanStatusService";
import { ToolIdentificationService } from "./ToolIdentificationService";

export class MetricsCollectorService {
    public static collectMetrics(input: IMetricsInput): IMetricsData {
        const severityCounts = this.parseSeverityCounts(input.severityCounts);
        const hasLogErrors = LogAnalysisService.hasErrors(input.output_logs);
        const scanStatus = ScanStatusService.determineScanStatus(
            input.scan_success,
            input.findings.length,
            hasLogErrors,
            input.output_logs
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