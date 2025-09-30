
export class LogAnalysisService {
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
}