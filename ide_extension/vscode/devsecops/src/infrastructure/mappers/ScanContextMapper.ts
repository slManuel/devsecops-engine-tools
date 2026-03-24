import { Finding } from "../../domain/model/Finding";
import { 
    IIacContext, 
    IImageScanContext, 
    IDependenciesScanContext,
    ISeverityCounts,
    Mappers 
} from "../../domain/model/mappers/Mappers";

export interface IScanResult {
    success: boolean;
    findings: Finding[];
    severityCounts: ISeverityCounts | null;
    normalOutput: string;
    errorMessage?: string;
}

/**
 * ScanContextMapper - Centralized mapper for scan contexts to findings
 * 
 * This mapper is agnostic of the execution source (Docker or Microservice).
 * Both executors must return JSON in the same format, which will be processed here.
 * 
 * Responsibilities:
 * - Extract context from stdout/output
 * - Parse raw context JSON
 * - Map context objects to Finding entities
 * - Extract severity counts
 * - Handle errors gracefully
 */
export class ScanContextMapper {
    private static readonly CONTEXT_REGEX = /===== BEGIN CONTEXT OUTPUT =====\s*([\s\S]*?)\s*===== END CONTEXT OUTPUT =====/;
    
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

    /**
     * Extracts and parses context output from stdout
     * Handles both wrapped (with markers) and unwrapped JSON
     */
    public static extractContextFromOutput(
        stdout: string, 
        scanType: 'image' | 'dependencies' | 'iac'
    ): IScanResult {
        const match = stdout.match(this.CONTEXT_REGEX);
        
        if (!match || !match[1]) {
            return {
                success: false,
                findings: [],
                severityCounts: null,
                normalOutput: stdout,
                errorMessage: 'No context data found in scanner output'
            };
        }

        let normalOutput = stdout.replace(this.CONTEXT_REGEX, '');
        
        try {
            const rawJson = match[1].trim();
            return this.parseAndMapContext(rawJson, scanType, normalOutput);
        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            return {
                success: false,
                findings: [],
                severityCounts: null,
                normalOutput,
                errorMessage: `Error parsing context JSON: ${errorMsg}`
            };
        }
    }

    /**
     * Parses raw context JSON and maps to findings
     * Used by both local scanners and remote microservice execution
     */
    public static parseAndMapContext(
        contextJson: string,
        scanType: 'image' | 'dependencies' | 'iac',
        normalOutput: string = ''
    ): IScanResult {
        try {
            const parsed = JSON.parse(contextJson) as any;
            
            // Extract context array based on scan type
            let contextArray: any[] = [];
            if (scanType === 'image' && parsed.container_context) {
                contextArray = parsed.container_context;
            } else if (scanType === 'dependencies' && parsed.dependencies_context) {
                contextArray = parsed.dependencies_context;
            } else if (scanType === 'iac' && parsed.iac_context) {
                contextArray = parsed.iac_context;
            } else if (Array.isArray(parsed)) {
                // Fallback: direct array
                contextArray = parsed;
            }

            // Map to findings based on scan type
            let findings: Finding[] = [];
            if (scanType === 'image') {
                findings = contextArray.map((ctx: IImageScanContext) => 
                    Mappers.mapImageScanContextToFinding(ctx)
                );
            } else if (scanType === 'dependencies') {
                findings = contextArray.map((ctx: IDependenciesScanContext) => 
                    Mappers.mapDependenciesScanContextToFinding(ctx)
                );
            } else if (scanType === 'iac') {
                findings = contextArray.map((ctx: IIacContext) => 
                    Mappers.mapIacContextToFinding(ctx)
                );
            }

            const severityCounts = this.calculateSeverityCounts(findings);

            return {
                success: true,
                findings,
                severityCounts,
                normalOutput
            };

        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            return {
                success: false,
                findings: [],
                severityCounts: null,
                normalOutput,
                errorMessage: `Error parsing context JSON: ${errorMsg}`
            };
        }
    }
}
