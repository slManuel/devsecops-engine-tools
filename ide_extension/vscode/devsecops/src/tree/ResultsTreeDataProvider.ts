import * as vscode from "vscode";
import { ScanResultItem } from "./results/ScanResultItem";
import { Finding } from "../domain/model/Finding";
import { FindingItem } from "./results/finding/FindingItem";

export class ResultsTreeDataProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<vscode.TreeItem | undefined | null | void> = new vscode.EventEmitter<vscode.TreeItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<vscode.TreeItem | undefined | null | void> = this._onDidChangeTreeData.event;
  private scanResults: ScanResultItem[] = [];
  private filterSeverities: Set<string> = new Set();
  private sortBySeverity: boolean = false;

  constructor(private context: vscode.ExtensionContext) {}

  public refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: vscode.TreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: vscode.TreeItem): Thenable<vscode.TreeItem[]> {
    if (!element) {
      return Promise.resolve(this.scanResults);
    }

    if (element instanceof ScanResultItem) {
      const children = element.getFilteredAndSortedChildren(
        this.filterSeverities,
        this.sortBySeverity
      );
      return Promise.resolve(children);
    }

    return Promise.resolve([]);
  }

  public addScanResult(
    label: string,
    findings: Finding[],
    sourceType: "iac" | "image" | "dependencies",
    scanPath?: string,
    outputChannel?: vscode.OutputChannel
  ): void {
    const timestamp = new Date();
    const findingItems = findings.map((f) => new FindingItem(f, scanPath, sourceType));

    this.scanResults.unshift(
      new ScanResultItem(label, sourceType, timestamp, findingItems, false, undefined, outputChannel)
    );

    this.refresh();
  }

  /**
   * Adds a loading placeholder scan result
   * @returns The scan ID to use for updating later
   */
  public addLoadingScanResult(
    label: string,
    sourceType: "iac" | "image" | "dependencies",
    outputChannel?: vscode.OutputChannel
  ): string {
    const timestamp = new Date();
    const scanItem = new ScanResultItem(label, sourceType, timestamp, [], true, undefined, outputChannel);

    this.scanResults.unshift(scanItem);
    this.refresh();

    return scanItem.scanId;
  }

  /**
   * Updates a loading scan result with actual findings
   */
  public updateScanResult(
    scanId: string,
    findings: Finding[],
    sourceType: "iac" | "image" | "dependencies",
    scanPath?: string
  ): void {
    const scanItem = this.scanResults.find(item => item.scanId === scanId);
    
    if (scanItem) {
      const findingItems = findings.map((f) => new FindingItem(f, scanPath, sourceType));
      scanItem.updateWithResults(findingItems);
      this.refresh();
    }
  }

  /**
   * Removes a scan result by its ID (useful if scan fails)
   */
  public removeScanResult(scanId: string): void {
    const index = this.scanResults.findIndex(item => item.scanId === scanId);
    if (index > -1) {
      const scanItem = this.scanResults[index];
      scanItem.dispose(); // Dispose the output channel
      this.scanResults.splice(index, 1);
      this.refresh();
    }
  }

  public deleteScanResult(scanResult: ScanResultItem): void {
    const index = this.scanResults.indexOf(scanResult);
    if (index > -1) {
      scanResult.dispose(); // Dispose the output channel
      this.scanResults.splice(index, 1);
      this.refresh();
    }
  }

  /**
   * Set severity filters
   */
  public setFilterSeverities(severities: string[]): void {
    this.filterSeverities = new Set(severities.map(s => s.toLowerCase()));
    this.updateScanResultDescriptions();
    this.refresh();
  }

  /**
   * Toggle severity-based sorting
   */
  public toggleSort(): void {
    this.sortBySeverity = !this.sortBySeverity;
    this.updateScanResultDescriptions();
    this.refresh();
  }

  /**
   * Clear all filters and sorting
   */
  public clearFilters(): void {
    this.filterSeverities.clear();
    this.sortBySeverity = false;
    this.updateScanResultDescriptions();
    this.refresh();
  }

  /**
   * Get current filter state
   */
  public getFilterState(): { severities: string[]; sorted: boolean } {
    return {
      severities: Array.from(this.filterSeverities),
      sorted: this.sortBySeverity
    };
  }

  /**
   * Update descriptions of all scan results to reflect active filters
   */
  private updateScanResultDescriptions(): void {
    this.scanResults.forEach(scanResult => {
      scanResult.updateDescription(this.filterSeverities, this.sortBySeverity);
    });
  }
}
