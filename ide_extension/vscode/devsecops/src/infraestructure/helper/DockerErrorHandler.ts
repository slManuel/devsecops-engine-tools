import { OutputChannel } from "vscode";

// Types and Interfaces
export interface ErrorContext {
    imageTag?: string;
    containerImageName?: string;
    toolVersion?: string;
}

type ErrorHandler = string | ((context: ErrorContext, outputChannel: OutputChannel) => void);

const DOCKER_ERROR_MESSAGES: Record<string, ErrorHandler> = {
    "Cannot connect to the Docker daemon": " 🐋 Docker is not running or not accessible. Please start Docker and try again.",
    "Docker is not running": " 🐋 Docker is not running or not accessible. Please start Docker and try again.",
    "No such image": (context, outputChannel) => {
        if (context.imageTag) {
            outputChannel.appendLine(`Scanner image ${context.imageTag} not found locally. Attempting to download...`);
            outputChannel.appendLine('');
        }
    },
    "Unable to find image": "📦 Container image not found. The image will be downloaded automatically.",
    "Failed to download image": "🛜 Failed to download image. Please check your internet connection or Docker configuration.",
    "Failed to ensure scanner image": "🛜 Failed to download image. Please check your internet connection or Docker configuration.",
    "context deadline exceeded": "🛜 Failed to download image. Please check your internet connection or Docker configuration.",
    "i/o timeout": "🌐 Network timeout: Unable to reach Docker registry. Please check your internet connection and registry availability.",
    "Error response from daemon: Get": "🌐 Network error: Unable to reach Docker registry. Please check your internet connection and registry URL.",
    "manifest unknown": (context, outputChannel) => {
        if (context.containerImageName && context.toolVersion) {
            outputChannel.appendLine(`⚠️ Please verify that version ${context.toolVersion} exists for image ${context.containerImageName}. You may need to check available versions or update your configuration.`);
            outputChannel.appendLine('');
        }
    },
    "manifest is not known to the registry": (context, outputChannel) => {
        if (context.containerImageName && context.toolVersion) {
            outputChannel.appendLine(`⚠️ Please verify that version ${context.toolVersion} exists for image ${context.containerImageName}. You may need to check available versions or update your configuration.`);
            outputChannel.appendLine('');
        }
    },
    "unknown flag": "⚠️ Invalid Docker command: Unknown flag or option. Please check the Docker command syntax.",
    "unknown shorthand flag": "⚠️ Invalid Docker command: Unknown shorthand flag. Please verify the command flags.",
    "Command failed:": "❌ Error executing container command. Please check the command syntax and Docker configuration.",
    "docker: command not found": "❌ Docker command not found. Please ensure Docker is installed and in your PATH.",
    "permission denied": "🔒 Permission denied while accessing Docker. Please check your Docker permissions or run with appropriate privileges.",
    "error during connect": "🔌 Error connecting to Docker. Please verify Docker is running and accessible.",
    "request cancelled": () => { throw new Error("Scan operation cancelled."); }
};

export class DockerErrorHandler {
    private lastErrorKey: string | null = null;

    /**
     * Returns all Docker error patterns for reuse in metrics analysis.
     * This maintains single source of truth for Docker error detection.
     */
    public static getErrorPatterns(): string[] {
        return Object.keys(DOCKER_ERROR_MESSAGES);
    }

    handle(errorMessage: string, outputChannel: OutputChannel, context: ErrorContext = {}): void {
        const errorKey = this.findMatchingErrorKey(errorMessage);

        if (errorKey) {
            if (this.isDuplicateError(errorKey)) {
                return;
            }
            this.lastErrorKey = errorKey;
            this.executeErrorHandler(errorKey, context, outputChannel);
            return;
        }

        this.handleGenericError(errorMessage, context, outputChannel);
    }

    reset(): void {
        this.lastErrorKey = null;
    }

    private findMatchingErrorKey(errorMessage: string): string | null {
        for (const key in DOCKER_ERROR_MESSAGES) {
            if (errorMessage.includes(key)) {
                return key;
            }
        }
        return null;
    }

    private isDuplicateError(errorKey: string): boolean {
        return this.lastErrorKey === errorKey;
    }

    private executeErrorHandler(errorKey: string, context: ErrorContext, outputChannel: OutputChannel): void {
        const handler = DOCKER_ERROR_MESSAGES[errorKey];
        if (typeof handler === "string") {
            outputChannel.appendLine(handler);
        } else {
            handler(context, outputChannel);
        }
    }

    private handleGenericError(errorMessage: string, context: ErrorContext, outputChannel: OutputChannel): void {
        this.lastErrorKey = null;
        if (context.imageTag) {
            outputChannel.appendLine(`Error checking for scanner image ${context.imageTag}: ${errorMessage}`);
        } else {
            outputChannel.appendLine(`❌ Failed to ensure scanner image is available. Please verify that the specified image version exists.`);
        }
    }
}
