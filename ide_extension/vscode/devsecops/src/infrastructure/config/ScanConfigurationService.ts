import * as vscode from 'vscode';

/**
 * ScanConfigurationService - Manages scan execution configuration
 * 
 * Determines which execution mode to use (local Docker vs remote microservice)
 * based on VS Code settings and environment capabilities.
 */
export class ScanConfigurationService {
    private static readonly configSection = 'devsecops';
    private static readonly executionModeKey = 'scanExecutionMode';
    private static readonly microserviceUrlKey = 'microserviceUrl';

    /**
     * Gets the configured execution mode from VS Code settings
     * @returns 'local-docker' | 'remote-microservice' | 'auto'
     */
    public static getExecutionMode(): 'local-docker' | 'remote-microservice' | 'auto' {
        const config = vscode.workspace.getConfiguration(this.configSection);
        const mode = config.get<string>(this.executionModeKey, 'local-docker');
        
        if (mode === 'remote-microservice' || mode === 'auto') {
            return mode;
        }
        
        return 'local-docker';
    }

    /**
     * Gets the microservice URL from settings
     */
    public static getMicroserviceUrl(): string | undefined {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return config.get<string>(this.microserviceUrlKey);
    }

    /**
     * Checks if microservice mode is enabled
     */
    public static isMicroserviceEnabled(): boolean {
        const mode = this.getExecutionMode();
        return mode === 'remote-microservice' || mode === 'auto';
    }

    /**
     * Checks if local Docker mode is enabled
     */
    public static isLocalDockerEnabled(): boolean {
        const mode = this.getExecutionMode();
        return mode === 'local-docker' || mode === 'auto';
    }

    /**
     * Updates the execution mode in settings
     */
    public static async setExecutionMode(mode: 'local-docker' | 'remote-microservice' | 'auto'): Promise<void> {
        const config = vscode.workspace.getConfiguration(this.configSection);
        await config.update(this.executionModeKey, mode, vscode.ConfigurationTarget.Global);
    }

    /**
     * Updates the microservice URL in settings
     */
    public static async setMicroserviceUrl(url: string): Promise<void> {
        const config = vscode.workspace.getConfiguration(this.configSection);
        await config.update(this.microserviceUrlKey, url, vscode.ConfigurationTarget.Global);
    }

    /**
     * Validates microservice configuration
     */
    public static validateMicroserviceConfig(): { valid: boolean; error?: string } {
        const url = this.getMicroserviceUrl();
        
        if (!url) {
            return {
                valid: false,
                error: 'Microservice URL is not configured. Please set devsecops.microserviceUrl in settings.'
            };
        }

        try {
            new URL(url);
            return { valid: true };
        } catch {
            return {
                valid: false,
                error: 'Invalid microservice URL format. Please provide a valid HTTP(S) URL.'
            };
        }
    }

    /**
     * Checks if debug mode is enabled (shows detailed request/response logs)
     */
    public static getDebugMode(): boolean {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return config.get<boolean>('general.debugMode', false);
    }

    /**
     * Gets the scan timeout in milliseconds
     * @returns Timeout value in milliseconds (default: 600000 = 10 minutes)
     */
    public static getScanTimeout(): number {
        const config = vscode.workspace.getConfiguration(this.configSection);
        const timeoutSeconds = config.get<number>('general.timeout', 600);
        // Convert seconds to milliseconds
        return timeoutSeconds * 1000;
    }

    /**
     * Gets all scan-related configuration
     */
    public static getAllScanConfig(): {
        executionMode: 'local-docker' | 'remote-microservice' | 'auto';
        microserviceUrl: string | undefined;
        containerImageName: string | undefined;
        containerImageVersion: string | undefined;
        dependenciesToken: string | undefined;
        xrayMode: string | undefined;
        dependenciesTool: string | undefined;
        iacTool: string | undefined;
        timeout: number;
        debugMode: boolean;
    } {
        const config = vscode.workspace.getConfiguration(this.configSection);
        
        return {
            executionMode: this.getExecutionMode(),
            microserviceUrl: this.getMicroserviceUrl(),
            containerImageName: config.get<string>('general.imageToUse'),
            containerImageVersion: config.get<string>('general.imageVersion'),
            dependenciesToken: config.get<string>('dependencies.token'),
            xrayMode: config.get<string>('dependencies.xrayMode'),
            dependenciesTool: config.get<string>('dependencies.tool'),
            iacTool: config.get<string>('iac.tool'),
            timeout: this.getScanTimeout(),
            debugMode: this.getDebugMode()
        };
    }
}
