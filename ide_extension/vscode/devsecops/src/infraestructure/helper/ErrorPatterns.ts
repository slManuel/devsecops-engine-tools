import { DockerErrorHandler } from './DockerErrorHandler';

/**
 * Centralized error patterns configuration.
 * 
 * Architecture:
 * - Docker patterns retrieved from DockerErrorHandler via static method (single source of truth)
 * - Network and Configuration patterns defined here
 * - When NetworkErrorHandler is created, move network patterns there and export similarly
 */

export const ERROR_PATTERNS = {
    docker: DockerErrorHandler.getErrorPatterns(),

    network: [
        'context deadline exceeded',
        'i/o timeout',
        'network timeout',
        'network error',
        'unable to reach docker registry',
        'connection refused',
        'connection timed out',
        'dial tcp',
        'no route to host'
    ],

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
        'scan timed out'
    ]
} as const;

/**
 * Error pattern categories for type safety
 */
export type ErrorCategory = keyof typeof ERROR_PATTERNS;
