import { OutputChannel } from "vscode";
import { IScanExecutor } from "./IScanExecutor";
import { RemoteMicroserviceExecutor } from "./RemoteMicroserviceExecutor";
import { LocalDockerExecutor } from "./LocalDockerExecutor";
import { ScanConfigurationService } from "../config/ScanConfigurationService";

/**
 * ScanExecutionOrchestrator - Orchestrates scan execution strategy
 * 
 * This class acts as a strategy selector, determining which execution mode
 * to use (local Docker or remote microservice) based on configuration and
 * availability.
 * 
 * Responsibilities:
 * - Check configured execution mode
 * - Validate executor availability
 * - Select appropriate executor
 * - Provide fallback mechanisms
 */
export class ScanExecutionOrchestrator {
    
    /**
     * Determines which executor should be used for the scan
     * @returns The appropriate IScanExecutor implementation
     */
    public static async selectExecutor(): Promise<IScanExecutor> {
        const executionMode = ScanConfigurationService.getExecutionMode();

        switch (executionMode) {
            case 'remote-microservice':
                return await this.tryRemoteMicroserviceOrFallback();
            
            case 'local-docker':
                return new LocalDockerExecutor();
            
            case 'auto': {
                // Try remote first, fallback to local
                const remoteExecutor = await this.tryRemoteMicroservice();
                if (remoteExecutor) {
                    return remoteExecutor;
                }
                // Fallback to local Docker
                return new LocalDockerExecutor();
            }
            
            default:
                return new LocalDockerExecutor();
        }
    }

    /**
     * Attempts to create and validate a remote microservice executor
     * @returns RemoteMicroserviceExecutor if available, null otherwise
     */
    private static async tryRemoteMicroservice(): Promise<IScanExecutor | null> {
        const validation = ScanConfigurationService.validateMicroserviceConfig();
        
        if (!validation.valid) {
            console.warn(`Remote microservice not available: ${validation.error}`);
            return null;
        }

        const executor = new RemoteMicroserviceExecutor();
        const canExecute = await executor.canExecute();
        
        if (!canExecute) {
            console.warn('Remote microservice executor validation failed');
            return null;
        }

        return executor;
    }

    /**
     * Tries remote microservice and falls back to local Docker if not available
     */
    private static async tryRemoteMicroserviceOrFallback(): Promise<IScanExecutor> {
        const remote = await this.tryRemoteMicroservice();
        if (remote) {
            return remote;
        }
        
        // Fallback to local Docker
        console.warn('Remote microservice not available, falling back to local Docker');
        return new LocalDockerExecutor();
    }

    /**
     * Gets a user-friendly message about the current execution mode status
     */
    public static async getExecutionModeStatus(outputChannel?: OutputChannel): Promise<string> {
        const executionMode = ScanConfigurationService.getExecutionMode();
        const executor = await this.selectExecutor();
        const actualMode = executor.getExecutionMode();
        
        let message = '';

        if (actualMode === 'remote-microservice') {
            message = '🌐 Using remote microservice execution mode';
        } else if (executionMode === 'remote-microservice') {
            message = '⚠️  Remote microservice mode is selected but not available.\n' +
                     'Falling back to local Docker execution.';
        } else if (executionMode === 'auto') {
            message = '🔄 Auto mode: Using local Docker';
        } else {
            message = '🐳 Using local Docker execution mode';
        }

        if (outputChannel) {
            outputChannel.appendLine(message);
            outputChannel.appendLine('');
        }

        return message;
    }

    /**
     * Validates and logs execution mode (deprecated - kept for backward compatibility)
     * @deprecated Use getExecutionModeStatus() instead
     */
    public static async validateCanProceed(outputChannel: OutputChannel): Promise<void> {
        await this.getExecutionModeStatus(outputChannel);
    }
}
