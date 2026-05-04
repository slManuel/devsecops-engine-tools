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
     * @returns 'local-docker' | 'remote-microservice'
     */
    public static getExecutionMode(): 'local-docker' | 'remote-microservice' {
        const config = vscode.workspace.getConfiguration(this.configSection);
        const mode = config.get<string>(this.executionModeKey, 'local-docker');
        
        if (mode === 'remote-microservice') {
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
        return mode === 'remote-microservice';
    }

    /**
     * Checks if local Docker mode is enabled
     */
    public static isLocalDockerEnabled(): boolean {
        const mode = this.getExecutionMode();
        return mode === 'local-docker';
    }

    /**
     * Updates the execution mode in settings
     */
    public static async setExecutionMode(mode: 'local-docker' | 'remote-microservice'): Promise<void> {
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
     * Validates that a given engine tools version exists on PyPI.
     * Returns the version if valid, throws an error if not found.
     */
    public static async validateEngineToolsVersion(version: string): Promise<void> {
        const url = `https://pypi.org/pypi/devsecops-engine-tools/${version}/json`;
        let status: number;
        try {
            const response = await fetch(url, { method: 'GET' });
            status = response.status;
        } catch (error) {
            throw new Error(
                `Could not reach PyPI to validate engine tools version "${version}". Check your internet connection. Original error: ${
                    error instanceof Error ? error.message : String(error)
                }`
            );
        }

        if (status === 404) {
            throw new Error(
                `Engine tools version "${version}" does not exist on PyPI. Please check the version in settings.`
            );
        }

        if (status !== 200) {
            throw new Error(
                `Unexpected response from PyPI (HTTP ${status}) while validating engine tools version "${version}".`
            );
        }
    }

    /**
     * Gets the custom rules URL for fetching custom IaC validation rules
     */
    public static getCustomRulesUrl(): string | undefined {
        const config = vscode.workspace.getConfiguration(this.configSection);
        return config.get<string>('iac.customRulesUrl');
    }

    /**
     * Gets the optional custom remote config path configured by the user.
     * When set, the scanners mount this host directory inside the container
     * at /ms_remote_config and pass it as --remote_config_repo to the CLI.
     * When not set, the image's built-in docker_default_remote_config is used.
     */
    public static getCustomRemoteConfigPath(): string | undefined {
        const config = vscode.workspace.getConfiguration(this.configSection);
        const value = config.get<string>('general.customRemoteConfigPath');
        return value && value.trim() !== '' ? value.trim() : undefined;
    }

    /**
     * Checks if debug mode is enabled (shows detailed scan logs)
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
        executionMode: 'local-docker' | 'remote-microservice';
        microserviceUrl: string | undefined;
        containerImageName: string | undefined;
        engineToolsVersion: string | undefined;
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
            engineToolsVersion: config.get<string>('general.engineToolsVersion'),
            dependenciesToken: config.get<string>('dependencies.dependenciesToken'),
            xrayMode: config.get<string>('dependencies.xrayMode'),
            dependenciesTool: config.get<string>('dependencies.dependenciesTool'),
            iacTool: config.get<string>('iac.iacTool'),
            timeout: this.getScanTimeout(),
            debugMode: this.getDebugMode()
        };
    }
}
