import * as vscode from 'vscode';

export class ScanOutputLoader {
  private readonly outputChannel: vscode.OutputChannel;
  private intervalId: NodeJS.Timeout | null = null;
  private isRunning = false;
  private scanTarget = '';
  private startTime = 0;

  private static readonly LOADING_DOTS = ['', '.', '..', '...'];
  private static readonly SECURITY_ICONS = ['🔒', '🔐', '🔑', '🛡️', '🔍'];

  constructor(outputChannel: vscode.OutputChannel) {
    this.outputChannel = outputChannel;
  }

  /**
   * Generates a formatted, centered banner for the output channel.
   * @param title The main text line of the banner.
   * @param subtitle An optional second text line.
   * @returns A formatted string representing the banner.
   */
  private static createBanner(title: string, subtitle?: string): string {
    const BANNER_WIDTH = 120
    const innerWidth = BANNER_WIDTH - 2; // Width between the '║' characters

    const topBorder = `╔${'═'.repeat(innerWidth)}╗`;
    const bottomBorder = `╚${'═'.repeat(innerWidth)}╝`;
    const emptyLine = `║${' '.repeat(innerWidth)}║`;

    // Helper to center a line of text within the banner
    const centerText = (text: string): string => {
      const padding = innerWidth - text.length;
      const leftPadding = Math.floor(padding / 2);
      const rightPadding = padding - leftPadding;
      return `║${' '.repeat(leftPadding)}${text}${' '.repeat(rightPadding)}║`;
    };

    const bannerLines = [
      topBorder,
      emptyLine,
      centerText(title)
    ];

    if (subtitle) {
      bannerLines.push(centerText(subtitle));
    }

    bannerLines.push(emptyLine, bottomBorder);

    return bannerLines.join('\n');
  }

  public start(scanTarget: string): void {
    this.isRunning = true;
    this.scanTarget = scanTarget;
    this.startTime = Date.now();
    // Print the scan message once
    this.outputChannel.appendLine('');
    this.outputChannel.appendLine(`🛡️ DevSecOps Scanning ${this.scanTarget}...`);
    this.outputChannel.appendLine('');
    this.outputChannel.show();
    // Don't start continuous animation - just print once
  }

  private showContinuousLoop(): void {
    let dotIndex = 0;
    this.intervalId = setInterval(() => {
      if (!this.isRunning) {
        return;
      }
      // Move cursor up one line and clear it (VSCode OutputChannel does not support this, so we re-print the line)
      // Instead, print the scan message with animated dots on the same line (simulate by appending, but only update every 1s)
      const dots = ScanOutputLoader.LOADING_DOTS[dotIndex % ScanOutputLoader.LOADING_DOTS.length];
      // Remove the last scan message (not possible in OutputChannel), so just print again for now
      this.outputChannel.appendLine(`🛡️ DevSecOps Scanning ${this.scanTarget}${dots}`);
      dotIndex++;
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

    // Only show completion - processing results should be shown separately
    this.showCompleted(findingsCount, scanType);
  }


  //Show completion message after all results are processed
  public showCompleted(findingsCount?: number, scanType?: string): void {
    const completionBanner = ScanOutputLoader.createBanner(
      'Scan Completed!',
      'Thank you for using DevSecOps Engine Tools Extension'
    );

    this.outputChannel.appendLine('');
    this.outputChannel.appendLine('✅ PHASE: COMPLETED');
    if (findingsCount !== undefined && scanType) {
      this.outputChannel.appendLine(`   └─ Found ${findingsCount} ${scanType} issues`);
    }
    this.outputChannel.appendLine('');
    this.outputChannel.appendLine(completionBanner);
  }

  public showError(error: string): void {
    this.stop();

    const errorBanner = ScanOutputLoader.createBanner('⚠️ ERROR ⚠️');

    this.outputChannel.appendLine('');
    this.outputChannel.appendLine(errorBanner);
    this.outputChannel.appendLine('');
    this.outputChannel.appendLine(`❌ ${error}`);
    this.outputChannel.appendLine('');
  }
}