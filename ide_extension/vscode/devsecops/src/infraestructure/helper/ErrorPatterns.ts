import { DockerErrorHandler } from './DockerErrorHandler';
import { NetworkErrorHandler } from './NetworkErrorHandler';

/**
 * Centralized error patterns configuration.
 * 
 * Architecture:
 * - Docker patterns retrieved from DockerErrorHandler via static method (single source of truth)
 * - Network patterns retrieved from NetworkErrorHandler via static method (single source of truth)
 * - Configuration patterns defined here
 */

export const ERROR_PATTERNS = {
    docker: DockerErrorHandler.getErrorPatterns(),

    network: NetworkErrorHandler.getErrorPatterns(),

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

/**
 * Error pattern categories for type safety
 */
export type ErrorCategory = keyof typeof ERROR_PATTERNS;
