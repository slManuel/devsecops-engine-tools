import { OutputChannel } from "vscode";

// Types and Interfaces
export interface ErrorContext {
    imageTag?: string;
    containerImageName?: string;
    toolVersion?: string;
}

type ErrorHandler = string | ((context: ErrorContext, outputChannel: OutputChannel) => void);

const NETWORK_ERROR_MESSAGES: Record<string, ErrorHandler> = {
    "context deadline exceeded": "🛜 VPN disconnected during download: Connection timeout detected. Please reconnect to VPN and try again.",
    "i/o timeout": "🌐 Network timeout: Unable to reach Docker registry. Please check your VPN connection and registry availability.",
    "connection refused": "🌐 Network connection refused: Unable to reach the registry. Verify VPN is active and properly configured.",
    "no route to host": "🌐 Network routing error: Cannot reach registry host. Check VPN connection and network configuration.",
    "no such host": "🌐 DNS lookup failed: Cannot resolve hostname. Ensure VPN is connected to access internal registry.",
    "network is unreachable": "🌐 Network unreachable: VPN may be inactive or disconnected. Please verify network connectivity.",
    "TLS handshake timeout": "🛜 VPN connection issue: TLS handshake timeout. Reconnect to VPN and retry.",
    "dial tcp": "🌐 Network connection error: Cannot establish connection to registry. Ensure VPN is active."
};

export class NetworkErrorHandler {
    private lastErrorKey: string | null = null;
    private lastErrorDetected: boolean = false;

    public static getErrorPatterns(): string[] {
        return Object.keys(NETWORK_ERROR_MESSAGES);
    }

    public hasNetworkError(): boolean {
        return this.lastErrorDetected;
    }

    handle(errorMessage: string, outputChannel: OutputChannel, context: ErrorContext = {}, logCapture?: (message: string) => void): void {
        const errorKey = this.findMatchingErrorKey(errorMessage);

        if (errorKey) {
            if (this.isDuplicateError(errorKey)) {
                return;
            }
            this.lastErrorKey = errorKey;
            this.lastErrorDetected = true;
            this.logRawError(errorMessage, outputChannel);
            this.executeErrorHandler(errorKey, context, outputChannel, logCapture);
            return;
        }

        this.handleGenericError(errorMessage, context, outputChannel);
        this.lastErrorDetected = false;
    }

    reset(): void {
        this.lastErrorKey = null;
        this.lastErrorDetected = false;
    }

    private findMatchingErrorKey(errorMessage: string): string | null {
        for (const key in NETWORK_ERROR_MESSAGES) {
            if (errorMessage.includes(key)) {
                return key;
            }
        }
        return null;
    }

    private isDuplicateError(errorKey: string): boolean {
        return this.lastErrorKey === errorKey;
    }

    private executeErrorHandler(errorKey: string, context: ErrorContext, outputChannel: OutputChannel, logCapture?: (message: string) => void): void {
        const handler = NETWORK_ERROR_MESSAGES[errorKey];
        if (typeof handler === "string") {
            outputChannel.appendLine(handler);
            if (logCapture) {
                logCapture(handler);
            }
        } else {
            handler(context, outputChannel);
        }
    }

    private logRawError(errorMessage: string, outputChannel: OutputChannel): void {
        const firstLine = errorMessage.split('\n')[0].trim();
        if (firstLine) {
            outputChannel.appendLine(`[Raw Error] ${firstLine}`);
        }
    }

    private handleGenericError(errorMessage: string, context: ErrorContext, outputChannel: OutputChannel): void {
        this.lastErrorKey = null;
        outputChannel.appendLine(`🌐 Network error: ${errorMessage}. Please check your VPN and internet connection.`);
    }
}
