/**
 * Service responsible for analyzing output logs from scanning processes.
 * Handles error detection, message extraction, and log pattern matching.
 */
export class LogAnalysisService {

    /**
     * Check if logs contain error indicators
     * @param logs Array of log messages from the scan process
     * @returns true if errors are detected, false otherwise
     */
    public static hasErrors(logs: string[]): boolean {
        if (!logs || logs.length === 0) {
            return false;
        }

        const errorPatterns = [
            'SCAN Error',
            'engine_core Error',
            'Error executing container command',
            'Failed to ensure scanner image',
            'Container not found',
            'Scan timed out',
            'No Dependencies Token provided'
        ];

        return logs.some(log =>
            errorPatterns.some(pattern => log.includes(pattern))
        );
    }

    /**
     * Extract exception or summary message from logs
     * @param logs Array of log messages
     * @param findingsCount Number of findings for fallback message
     * @param providedMessage Optional pre-provided message
     * @returns Extracted or generated exception message
     */
    public static extractExceptionMessage(
        logs: string[],
        findingsCount: number,
        providedMessage?: string
    ): string {
        // Use provided message if available
        if (providedMessage) {
            return providedMessage;
        }

        // Look for specific patterns in logs
        if (logs && logs.length > 0) {
            // Look for "Found X issues in scan" pattern
            const foundMessage = logs.find(log =>
                log.includes('Found') && log.includes('issues in scan')
            );
            if (foundMessage) {
                return foundMessage;
            }

            // Look for error messages
            const errorMessage = logs.find(log =>
                log.includes('Error') ||
                log.includes('Failed') ||
                log.includes('timeout')
            );
            if (errorMessage) {
                return errorMessage;
            }
        }

        // Default fallback message
        return `Found ${findingsCount} issues in scan`;
    }

    /**
     * Get all error messages from logs
     * @param logs Array of log messages
     * @returns Array of error messages found in logs
     */
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

    /**
     * Check if logs indicate a successful scan
     * @param logs Array of log messages
     * @returns true if scan appears successful based on logs
     */
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
}