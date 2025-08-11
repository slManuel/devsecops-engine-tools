import * as vscode from 'vscode';

export interface SimpleLoadingOptions {
  message?: string;
  showPercentage?: boolean;
  showElapsedTime?: boolean;
}

export class SimpleProgressLoader {
  private readonly outputChannel: vscode.OutputChannel;
  private intervalId: NodeJS.Timeout | null = null;
  private currentProgress = 0;
  private startTime: number = 0;
  private isRunning = false;
  private currentMessage = '';

  private static readonly SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
  private static readonly DOTS = ['   ', '.  ', '.. ', '...'];

  private static readonly BANNER = `
╔══════════════════════════════════════════════════════════════╗
║                     🛡️  DevSecOps Engine                    ║ 
║                    Security Scan in Progress                 ║
╚══════════════════════════════════════════════════════════════╝
`;

  private static readonly COMPLETION_BANNER = `
╔══════════════════════════════════════════════════════════════╗
║                     ✅ Scan Completed!                       ║
║                   Thank you for using DevSecOps              ║
╚══════════════════════════════════════════════════════════════╝
`;

  constructor(outputChannel: vscode.OutputChannel) {
    this.outputChannel = outputChannel;
  }

  /**
   * Start the simple progress loader
   */
  public start(options: SimpleLoadingOptions = {}): void {
    if (this.isRunning) {
      this.stop();
    }

    const {
      message = 'DevSecOps Scanning',
      showPercentage = true,
      showElapsedTime = true
    } = options;

    this.isRunning = true;
    this.startTime = Date.now();
    this.currentProgress = 0;
    this.currentMessage = message;

    // Show initial banner
    this.outputChannel.clear();
    this.outputChannel.appendLine(SimpleProgressLoader.BANNER);
    this.outputChannel.appendLine('');

    let frameIndex = 0;
    let dotIndex = 0;

    this.intervalId = setInterval(() => {
      if (!this.isRunning) return;

      // Auto-increment progress (simulate work being done)
      this.currentProgress = Math.min(this.currentProgress + 1, 100);
      
      // Create the progress bar
      const progressBar = this.createProgressBar(this.currentProgress);
      const spinner = SimpleProgressLoader.SPINNER_FRAMES[frameIndex % SimpleProgressLoader.SPINNER_FRAMES.length];
      const dots = SimpleProgressLoader.DOTS[dotIndex % SimpleProgressLoader.DOTS.length];
      
      // Build the status line
      let statusLine = `🔒 ${this.currentMessage}${dots}`;
      
      if (showPercentage) {
        statusLine += ` ${progressBar}`;
      } else {
        statusLine += ` ${spinner}`;
      }
      
      if (showElapsedTime) {
        statusLine += this.getElapsedTimeString();
      }

      // Clear and redraw the progress line
      this.outputChannel.clear();
      this.outputChannel.appendLine(SimpleProgressLoader.BANNER);
      this.outputChannel.appendLine('');
      this.outputChannel.append(statusLine);

      frameIndex++;
      dotIndex++;

      // If we reach 100%, stop automatically
      if (this.currentProgress >= 100) {
        setTimeout(() => this.stop(), 500);
      }
    }, 150);

    this.outputChannel.show();
  }

  /**
   * Set specific progress percentage
   */
  public setProgress(percentage: number, message?: string): void {
    if (!this.isRunning) return;
    
    this.currentProgress = Math.max(0, Math.min(100, percentage));
    if (message) {
      this.currentMessage = message;
    }
  }

  /**
   * Update the message
   */
  public updateMessage(newMessage: string): void {
    if (!this.isRunning) return;
    this.currentMessage = newMessage;
  }

  /**
   * Add a status update below the progress bar
   */
  public addStatusUpdate(status: string): void {
    if (!this.isRunning) return;
    
    this.outputChannel.appendLine('');
    this.outputChannel.appendLine(`📝 ${status}`);
  }

  /**
   * Stop the loading animation
   */
  public stop(showCompletion = true): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    
    this.isRunning = false;
    this.currentProgress = 100;

    if (showCompletion) {
      // Show final state
      const finalProgressBar = this.createProgressBar(100);
      this.outputChannel.clear();
      this.outputChannel.appendLine(SimpleProgressLoader.BANNER);
      this.outputChannel.appendLine('');
      this.outputChannel.appendLine(`✅ ${this.currentMessage} Complete! ${finalProgressBar}`);
      this.outputChannel.appendLine('');
      this.outputChannel.appendLine(SimpleProgressLoader.COMPLETION_BANNER);
    }
  }

  /**
   * Show error state
   */
  public showError(error: string): void {
    this.stop(false);
    
    this.outputChannel.appendLine('');
    this.outputChannel.appendLine('╔══════════════════════════════════════════════════════════════╗');
    this.outputChannel.appendLine('║                        ⚠️  ERROR                              ║');
    this.outputChannel.appendLine('╚══════════════════════════════════════════════════════════════╝');
    this.outputChannel.appendLine('');
    this.outputChannel.appendLine(`❌ ${error}`);
  }

  private createProgressBar(percentage: number, width = 25): string {
    const filled = Math.floor((percentage / 100) * width);
    const empty = width - filled;
    
    const filledBar = '█'.repeat(filled);
    const emptyBar = '░'.repeat(empty);
    
    return `[${filledBar}${emptyBar}] ${percentage.toString().padStart(3)}%`;
  }

  private getElapsedTimeString(): string {
    const elapsed = Date.now() - this.startTime;
    const seconds = Math.floor(elapsed / 1000);
    return ` (${seconds}s)`;
  }

  /**
   * Static method for simple loading with automatic progress
   */
  public static async withAutoProgress<T>(
    outputChannel: vscode.OutputChannel,
    operation: (loader: SimpleProgressLoader) => Promise<T>,
    options: SimpleLoadingOptions = {}
  ): Promise<T> {
    const loader = new SimpleProgressLoader(outputChannel);
    
    try {
      loader.start(options);
      const result = await operation(loader);
      loader.stop();
      return result;
    } catch (error) {
      loader.showError(error instanceof Error ? error.message : String(error));
      throw error;
    }
  }
}

// Quick utility function
export const createSimpleLoader = (outputChannel: vscode.OutputChannel, message?: string) => {
  const loader = new SimpleProgressLoader(outputChannel);
  loader.start({ 
    message: message || 'DevSecOps Scanning',
    showPercentage: true,
    showElapsedTime: true 
  });
  return loader;
};
