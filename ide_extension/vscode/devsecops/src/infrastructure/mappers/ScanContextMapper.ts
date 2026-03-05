import { Finding } from "../../domain/model/Finding";
import { 
    IIacContext, 
    IImageScanContext, 
    IDependenciesScanContext,
    ISeverityCounts,
    Mappers 
} from "../../domain/model/mappers/Mappers";

/**
 * ScanContextMapper - Centralized mapper for scan contexts to findings
 * 
 * This mapper is agnostic of the execution source (Docker or Microservice).
 * Both executors must return JSON in the same format, which will be processed here.
 * 
 * Responsibilities:
 * - Parse raw context JSON
 * - Map context objects to Finding entities
 * - Extract severity counts
 * - Handle errors gracefully
 */
export class ScanContextMapper {
    
    /**
     * Maps Image scan context JSON to findings
     */
    public static mapImageScanContext(contextJson: string): { findings: Finding[]; severityCounts: ISeverityCounts | null } {
        try {
            const parsed = JSON.parse(contextJson) as unknown;
            
            if (!parsed || !Array.isArray(parsed)) {
                return { findings: [], severityCounts: null };
            }

            const findings: Finding[] = parsed.map((context: IImageScanContext) => 
                Mappers.mapImageScanContextToFinding(context)
            );

            const severityCounts = this.calculateSeverityCounts(findings);

            return { findings, severityCounts };
        } catch (error) {
            console.error('Error mapping image scan context:', error);
            return { findings: [], severityCounts: null };
        }
    }

    /**
     * Maps Dependencies scan context JSON to findings
     */
    public static mapDependenciesScanContext(contextJson: string): { findings: Finding[]; severityCounts: ISeverityCounts | null } {
        try {
            const parsed = JSON.parse(contextJson) as unknown;
            
            if (!parsed || !Array.isArray(parsed)) {
                return { findings: [], severityCounts: null };
            }

            const findings: Finding[] = parsed.map((context: IDependenciesScanContext) => 
                Mappers.mapDependenciesScanContextToFinding(context)
            );

            const severityCounts = this.calculateSeverityCounts(findings);

            return { findings, severityCounts };
        } catch (error) {
            console.error('Error mapping dependencies scan context:', error);
            return { findings: [], severityCounts: null };
        }
    }

    /**
     * Maps IaC scan context JSON to findings
     */
    public static mapIacScanContext(contextJson: string): { findings: Finding[]; severityCounts: ISeverityCounts | null } {
        try {
            const parsed = JSON.parse(contextJson) as unknown;
            
            if (!parsed || !Array.isArray(parsed)) {
                return { findings: [], severityCounts: null };
            }

            const findings: Finding[] = parsed.map((context: IIacContext) => 
                Mappers.mapIacContextToFinding(context)
            );

            const severityCounts = this.calculateSeverityCounts(findings);

            return { findings, severityCounts };
        } catch (error) {
            console.error('Error mapping IaC scan context:', error);
            return { findings: [], severityCounts: null };
        }
    }

    /**
     * Generic mapper that selects the appropriate scan type mapper
     */
    public static mapScanContext(
        contextJson: string, 
        scanType: 'image' | 'dependencies' | 'iac'
    ): { findings: Finding[]; severityCounts: ISeverityCounts | null } {
        switch (scanType) {
            case 'image':
                return this.mapImageScanContext(contextJson);
            case 'dependencies':
                return this.mapDependenciesScanContext(contextJson);
            case 'iac':
                return this.mapIacScanContext(contextJson);
            default:
                console.error(`Unknown scan type: ${String(scanType)}`);
                return { findings: [], severityCounts: null };
        }
    }

    /**
     * Calculates severity counts from findings
     */
    private static calculateSeverityCounts(findings: Finding[]): ISeverityCounts {
        const counts = {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
        };

        findings.forEach(finding => {
            const severity = finding.getSeverity().toLowerCase();
            if (severity === 'critical') {
                counts.critical++;
            } else if (severity === 'high') {
                counts.high++;
            } else if (severity === 'medium') {
                counts.medium++;
            } else if (severity === 'low') {
                counts.low++;
            }
        });

        return {
            critical: counts.critical.toString(),
            high: counts.high.toString(),
            medium: counts.medium.toString(),
            low: counts.low.toString()
        };
    }

    /**
     * Validates if context JSON is in the expected format
     */
    public static validateContextJson(contextJson: string): boolean {
        try {
            const parsed = JSON.parse(contextJson) as unknown;
            return Array.isArray(parsed);
        } catch {
            return false;
        }
    }
}
