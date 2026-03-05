import { DockerService } from '../services/DockerService';
import { ErrorHandlingService } from '../services/ErrorHandlingService';


export const ERROR_PATTERNS = {
    
    docker: DockerService.getErrorPatterns(),
    network: ErrorHandlingService.getNetworkErrorPatterns(),

    configuration: [
        'no dependencies token provided',
        'invalid configuration',
        'unknown flag',
        'unknown shorthand flag',
        'invalid docker command'
    ],

    general: [
        'scan error',
        'engine_core error',
        'error executing container command',
        'failed to ensure scanner image',
        'container not found',
        'scan timed out',
        'command failed'
    ]
} as const;

export type ErrorCategory = keyof typeof ERROR_PATTERNS;
