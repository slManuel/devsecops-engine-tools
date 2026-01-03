
import { ERROR_PATTERNS } from "./ErrorPatterns";

export class LogAnalysisService {
    /**
     * Check if logs contain any general error patterns
     */
    public static hasErrors(logs: string[]): boolean {
        if (!logs || logs.length === 0) {
            return false;
        }

        return logs.some(log => {
            const logLower = log.toLowerCase();
            return ERROR_PATTERNS.general.some(pattern => logLower.includes(pattern));
        });
    }

    public static extractExceptionMessage(
        logs: string[],
        findingsCount: number,
        providedMessage?: string
    ): string {
        if (providedMessage) {
            return providedMessage;
        }

        if (logs && logs.length > 0) {
            const foundMessage = logs.find(log =>
                log.includes('Found') && log.includes('issues in scan')
            );
            if (foundMessage) {
                return foundMessage;
            }

            const errorMessage = logs.find(log =>
                log.includes('Error') ||
                log.includes('Failed') ||
                log.includes('timeout')
            );
            if (errorMessage) {
                return errorMessage;
            }
        }

        return `Found ${findingsCount} issues in scan`;
    }

    public static getErrorMessages(logs: string[]): string[] {
        if (!logs || logs.length === 0) {
            return [];
        }

        return logs.filter(log =>
            log.includes('Error') ||
            log.includes('Failed') ||
            log.includes('timeout') ||
            log.includes('SCAN Error')
        );
    }

    public static indicatesSuccess(logs: string[]): boolean {
        if (!logs || logs.length === 0) {
            return false;
        }

        const successPatterns = [
            'Successfully extracted context data',
            '✔Succeeded',
            'PHASE: COMPLETED'
        ];

        return logs.some(log =>
            successPatterns.some(pattern => log.includes(pattern))
        );
    }

    /**
     * Check if logs contain Docker-specific errors
     * Uses shared ERROR_PATTERNS to maintain consistency with DockerErrorHandler
     */
    public static hasDockerErrors(logs: string[]): boolean {
        return this.hasErrorCategory(logs, 'docker');
    }

    /**
     * Check if logs contain Network-specific errors
     * Uses shared ERROR_PATTERNS
     */
    public static hasNetworkErrors(logs: string[]): boolean {
        return this.hasErrorCategory(logs, 'network');
    }

    /**
     * Check if logs contain Configuration-specific errors
     * Uses shared ERROR_PATTERNS
     */
    public static hasConfigurationErrors(logs: string[]): boolean {
        return this.hasErrorCategory(logs, 'configuration');
    }

    /**
     * Generic helper to check for error patterns by category
     * Promotes code reuse and maintainability
     */
    private static hasErrorCategory(logs: string[], category: keyof typeof ERROR_PATTERNS): boolean {
        if (!logs || logs.length === 0) {
            return false;
        }

        return logs.some(log => {
            const logLower = log.toLowerCase();
            return ERROR_PATTERNS[category].some(pattern =>
                logLower.includes(pattern.toLowerCase())
            );
        });
    }
}