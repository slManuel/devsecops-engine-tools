import { OutputChannel, Progress, ProgressLocation } from "vscode";

/**
 * UploadProgressTracker - Tracks and reports upload progress
 * 
 * Provides real-time progress updates including:
 * - Percentage completed
 * - Upload speed
 * - Estimated time remaining
 * - Visual progress bar (using VS Code native progress API)
 */
export class UploadProgressTracker {
    private totalBytes: number;
    private uploadedBytes: number = 0;
    private startTime: number;
    private lastUpdateTime: number = 0;
    private lastReportedPercentage: number = 0;
    private outputChannel: OutputChannel;
    private progressReporter?: Progress<{ message?: string; increment?: number }>;

    // Minimum file size to show progress (1MB)
    private static readonly MIN_SIZE_FOR_PROGRESS = 1024 * 1024;
    // Update interval (every 1% or 500ms, whichever comes first)
    private static readonly UPDATE_INTERVAL_MS = 500;
    private static readonly PERCENTAGE_THRESHOLD = 1;

    constructor(
        totalBytes: number, 
        outputChannel: OutputChannel,
        progressReporter?: Progress<{ message?: string; increment?: number }>
    ) {
        this.totalBytes = totalBytes;
        this.outputChannel = outputChannel;
        this.progressReporter = progressReporter;
        this.startTime = Date.now();
        this.lastUpdateTime = this.startTime;
    }

    /**
     * Check if progress reporting should be enabled for this file size
     */
    public static shouldShowProgress(fileSize: number): boolean {
        return fileSize >= this.MIN_SIZE_FOR_PROGRESS;
    }

    /**
     * Update progress with new bytes uploaded
     */
    public update(bytesUploaded: number): void {
        this.uploadedBytes = bytesUploaded;
        
        const now = Date.now();
        const timeSinceLastUpdate = now - this.lastUpdateTime;
        const percentage = Math.floor((this.uploadedBytes / this.totalBytes) * 100);
        const percentageDiff = percentage - this.lastReportedPercentage;

        // Only update if:
        // 1. Enough time has passed (UPDATE_INTERVAL_MS), OR
        // 2. Percentage increased by threshold, OR
        // 3. Upload is complete (100%)
        const shouldUpdate = 
            timeSinceLastUpdate >= UploadProgressTracker.UPDATE_INTERVAL_MS ||
            percentageDiff >= UploadProgressTracker.PERCENTAGE_THRESHOLD ||
            percentage >= 100;

        if (shouldUpdate) {
            this.reportProgress();
            this.lastUpdateTime = now;
            this.lastReportedPercentage = percentage;
        }
    }

    /**
     * Report current progress to output channel and/or VS Code progress API
     */
    private reportProgress(): void {
        const percentage = Math.floor((this.uploadedBytes / this.totalBytes) * 100);
        const elapsed = Date.now() - this.startTime;
        const speed = this.uploadedBytes / (elapsed / 1000); // bytes per second
        const remaining = this.totalBytes - this.uploadedBytes;
        const eta = remaining / speed; // seconds

        // Format values
        const uploadedMB = (this.uploadedBytes / (1024 * 1024)).toFixed(2);
        const totalMB = (this.totalBytes / (1024 * 1024)).toFixed(2);
        const speedFormatted = this.formatSpeed(speed);
        const etaFormatted = this.formatETA(eta);

        // If we have a progress reporter (VS Code native progress), use it
        if (this.progressReporter) {
            const message = `${uploadedMB}/${totalMB} MB • ${speedFormatted} • ETA: ${etaFormatted}`;
            const increment = percentage - this.lastReportedPercentage;
            
            this.progressReporter.report({
                message,
                increment
            });
        } else {
            // Fallback: use output channel with progress bar
            const progressBar = this.createProgressBar(percentage);
            const message = `📤 Uploading: ${progressBar} ${percentage}% | ${uploadedMB}/${totalMB} MB | ${speedFormatted} | ETA: ${etaFormatted}`;
            this.outputChannel.appendLine(message);
        }
    }

    /**
     * Create visual progress bar
     */
    private createProgressBar(percentage: number): string {
        const barLength = 20;
        const filledLength = Math.floor((percentage / 100) * barLength);
        const emptyLength = barLength - filledLength;
        
        const filled = '█'.repeat(filledLength);
        const empty = '░'.repeat(emptyLength);
        
        return `[${filled}${empty}]`;
    }

    /**
     * Format upload speed
     */
    private formatSpeed(bytesPerSecond: number): string {
        if (bytesPerSecond < 1024) {
            return `${bytesPerSecond.toFixed(0)} B/s`;
        } else if (bytesPerSecond < 1024 * 1024) {
            return `${(bytesPerSecond / 1024).toFixed(2)} KB/s`;
        } else {
            return `${(bytesPerSecond / (1024 * 1024)).toFixed(2)} MB/s`;
        }
    }

    /**
     * Format estimated time remaining
     */
    private formatETA(seconds: number): string {
        if (!isFinite(seconds) || seconds < 0) {
            return 'calculating...';
        }

        if (seconds < 60) {
            return `${Math.ceil(seconds)}s`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const secs = Math.ceil(seconds % 60);
            return `${minutes}m ${secs}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
    }

    /**
     * Mark upload as complete
     */
    public complete(): void {
        const elapsed = Date.now() - this.startTime;
        const totalMB = (this.totalBytes / (1024 * 1024)).toFixed(2);
        const avgSpeed = this.formatSpeed(this.totalBytes / (elapsed / 1000));
        const elapsedFormatted = this.formatETA(elapsed / 1000);

        // Always log completion to output channel
        this.outputChannel.appendLine(`✅ Upload complete: ${totalMB} MB in ${elapsedFormatted} (avg: ${avgSpeed})`);
        this.outputChannel.appendLine('');
    }

    /**
     * Report upload start
     */
    public start(): void {
        const totalMB = (this.totalBytes / (1024 * 1024)).toFixed(2);
        
        // Only log to output channel if not using native progress
        // (native progress will show in UI automatically)
        if (!this.progressReporter) {
            this.outputChannel.appendLine(`📤 Starting upload: ${totalMB} MB`);
        }
    }
}
