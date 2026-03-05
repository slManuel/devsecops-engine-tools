/**
 * Service responsible for identifying the scanning tool from findings.
 * Uses the same pattern as Mappers: finding.module || fallback
 */
export class ToolIdentificationService {

    /**
     * Determine tool name from findings using the same pattern as Mappers
     * @param findings Array of Finding objects from the scan
     * @param fallbackTool Fallback tool identifier (e.g., "engine_dependencies")
     * @returns The tool identifier
     */
    public static determine(findings: any[], fallbackTool?: string): string {
        if (findings && findings.length > 0) {
            const firstFinding = findings[0];
            if (firstFinding && firstFinding.module) {
                return firstFinding.module;
            }
        }

        // Fallback to provided tool or unknown
        return fallbackTool || 'unknown';
    }
}