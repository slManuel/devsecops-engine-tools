import * as vscode from 'vscode';

export class ScanOutputLoader {
  private readonly outputChannel: vscode.OutputChannel;
  private intervalId: NodeJS.Timeout | null = null;
  private isRunning = false;
  private scanTarget = '';
  private startTime = 0;

  private static readonly LOADING_DOTS = ['', '.', '..', '...'];

  private static readonly SECURITY_ICONS = ['🔒', '🔐', '🔑', '🛡️', '🔍'];

  private static readonly COMPLETION_BANNER = `
╔══════════════════════════════════════════════════════════════╗
║                     ✅ Scan Completed!                       ║
║             Thank you for using DevSecOps Engine Tools       ║
╚══════════════════════════════════════════════════════════════╝
`;

  constructor(outputChannel: vscode.OutputChannel) {
    this.outputChannel = outputChannel;
  }

  /**
   * Start the loading animation - show continuous loop until stopped
   */
  public start(scanTarget: string): void {
    if (this.isRunning) {
      this.stop();
    }

    this.isRunning = true;
    this.scanTarget = scanTarget;
    this.startTime = Date.now();

    // Show continuous looping animation
    this.showContinuousLoop();

    this.outputChannel.show();
  }

  private showContinuousLoop(): void {
    this.intervalId = setInterval(() => {
      if (!this.isRunning) {
        return;
      }

      // Calculate elapsed time in seconds
      const elapsedSeconds = Math.floor((Date.now() - this.startTime) / 1000);

      const dotsIndex = elapsedSeconds % 4;
      const loadingDots = ScanOutputLoader.LOADING_DOTS[dotsIndex];

      const iconIndex = Math.floor(elapsedSeconds / 3) % ScanOutputLoader.SECURITY_ICONS.length;
      const securityIcon = ScanOutputLoader.SECURITY_ICONS[iconIndex];

      // Clear and show current status
      this.outputChannel.clear();
      this.outputChannel.appendLine(`${securityIcon} DevSecOps Scanning ${this.scanTarget}${loadingDots}`);
      this.outputChannel.appendLine(`⏱️ Time Elapsed: ${elapsedSeconds}s`);

    }, 1000);
  }

  public stop(findingsCount?: number, scanType?: string): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    this.isRunning = false;

    // If called without parameters, just stop animation silently (scan output will appear)
    if (findingsCount === undefined && scanType === undefined) {
      return;
    }

    this.outputChannel.appendLine('');
    this.outputChannel.appendLine('✅ PHASE: COMPLETED');
    if (findingsCount !== undefined && scanType) {
      this.outputChannel.appendLine(`   └─ Found ${findingsCount} ${scanType} issues`);
    }
    this.outputChannel.appendLine('');
    this.outputChannel.appendLine(ScanOutputLoader.COMPLETION_BANNER);
  }

  public showError(error: string): void {
    this.stop();

    this.outputChannel.appendLine('');
    this.outputChannel.appendLine('╔══════════════════════════════════════════════════════════════╗');
    this.outputChannel.appendLine('║                        ⚠️  ERROR                             ║');
    this.outputChannel.appendLine('╚══════════════════════════════════════════════════════════════╝');
    this.outputChannel.appendLine('');
    this.outputChannel.appendLine(`❌ ${error}`);
    this.outputChannel.appendLine('');
  }
}
