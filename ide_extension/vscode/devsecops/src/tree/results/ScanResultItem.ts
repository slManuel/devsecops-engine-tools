import * as vscode from "vscode";
import { FindingItem } from "./finding/FindingItem";

export class ScanResultItem extends vscode.TreeItem {
  public isLoading: boolean = false;
  public scanId: string;
  public outputChannel?: vscode.OutputChannel;

  constructor(
    public readonly label: string,
    public sourceType: string,
    public readonly timestamp: Date,
    public children: vscode.TreeItem[],
    isLoading: boolean = false,
    scanId?: string,
    outputChannel?: vscode.OutputChannel
  ) {
    super(label, isLoading ? vscode.TreeItemCollapsibleState.None : vscode.TreeItemCollapsibleState.Collapsed);
    this.isLoading = isLoading;
    this.scanId = scanId || `scan-${Date.now()}-${Math.random()}`;
    this.sourceType = sourceType;
    this.outputChannel = outputChannel;
    
    if (isLoading) {
      this.tooltip = `${label} - Scanning in progress...`;
      this.description = "⏳ Scanning...";
      this.iconPath = new vscode.ThemeIcon("sync~spin", new vscode.ThemeColor("charts.blue"));
      this.contextValue = "scanResult-loading";
    } else {
      this.tooltip = `${label} - ${children.length} findings`;
      this.description = `${children.length} findings - ${timestamp.toLocaleString()}`;
      this.iconPath = children.length > 0
        ? new vscode.ThemeIcon("warning", new vscode.ThemeColor("errorForeground"))
        : new vscode.ThemeIcon("pass", new vscode.ThemeColor("terminal.ansiGreen"));
      this.contextValue = "scanResult";
    }
  }

  public updateWithResults(findings: vscode.TreeItem[]): void {
    this.isLoading = false;
    this.children = findings;
    this.collapsibleState = vscode.TreeItemCollapsibleState.Collapsed;
    this.tooltip = `${this.label} - ${findings.length} findings`;
    this.description = `${findings.length} findings - ${this.timestamp.toLocaleString()}`;
    this.iconPath = findings.length > 0
      ? new vscode.ThemeIcon("warning", new vscode.ThemeColor("errorForeground"))
      : new vscode.ThemeIcon("pass", new vscode.ThemeColor("terminal.ansiGreen"));
    this.contextValue = "scanResult";
  }

  public dispose(): void {
    if (this.outputChannel) {
      this.outputChannel.dispose();
      this.outputChannel = undefined;
    }
  }

  /**
   * Get children filtered and sorted according to current settings
   */
  public getFilteredAndSortedChildren(
    filterSeverities: Set<string>,
    sortBySeverity: boolean
  ): vscode.TreeItem[] {
    let filteredChildren = this.children;

    // Apply severity filter
    if (filterSeverities.size > 0) {
      filteredChildren = this.children.filter(child => {
        if (child instanceof FindingItem) {
          const severity = child.finding.getSeverity().toLowerCase();
          return filterSeverities.has(severity);
        }
        return true;
      });
    }

    // Apply sorting by severity
    if (sortBySeverity) {
      const severityOrder: Record<string, number> = {
        critical: 0,
        high: 1,
        medium: 2,
        low: 3
      };

      filteredChildren = [...filteredChildren].sort((a, b) => {
        if (a instanceof FindingItem && b instanceof FindingItem) {
          const severityA = a.finding.getSeverity().toLowerCase();
          const severityB = b.finding.getSeverity().toLowerCase();
          const orderA = severityOrder[severityA] ?? 999;
          const orderB = severityOrder[severityB] ?? 999;
          return orderA - orderB;
        }
        return 0;
      });
    }

    return filteredChildren;
  }

  /**
   * Update description to reflect active filters
   */
  public updateDescription(filterSeverities: Set<string>, sortBySeverity: boolean): void {
    if (this.isLoading) {
      return; // Don't update if still loading
    }

    const totalFindings = this.children.length;
    const filteredChildren = this.getFilteredAndSortedChildren(filterSeverities, sortBySeverity);
    const visibleFindings = filteredChildren.length;

    let description = `${totalFindings} findings`;

    // Add filter indicator
    if (filterSeverities.size > 0) {
      const severityLabels = Array.from(filterSeverities)
        .map(s => s.charAt(0).toUpperCase() + s.slice(1))
        .join(', ');
      description = `${visibleFindings}/${totalFindings} findings [Filter: ${severityLabels}]`;
    } else if (visibleFindings !== totalFindings) {
      description = `${visibleFindings}/${totalFindings} findings`;
    }

    // Add sort indicator
    if (sortBySeverity) {
      description += ' [Sorted]';
    }

    description += ` - ${this.timestamp.toLocaleString()}`;
    this.description = description;
    this.tooltip = `${this.label} - ${description}`;
  }
}