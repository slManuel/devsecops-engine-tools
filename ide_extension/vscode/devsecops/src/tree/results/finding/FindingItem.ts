import * as vscode from "vscode";

export class FindingItem extends vscode.TreeItem {
  constructor(
    public readonly finding: any // Using any for now, replace with proper type from your ScannerRes
  ) {
    super(finding.description || "Unknown Issue", vscode.TreeItemCollapsibleState.None);
    this.description = finding.severity || "Unknown";
    this.tooltip = `${finding.description}\nSeverity: ${finding.severity}\nResource: ${finding.resource || "Unknown"}`;
    
    // Set icon based on severity
    switch (finding.severity?.toLowerCase()) {
      case "critical":
      case "high":
        this.iconPath = new vscode.ThemeIcon("error");
        break;
      case "medium":
        this.iconPath = new vscode.ThemeIcon("warning");
        break;
      case "low":
        this.iconPath = new vscode.ThemeIcon("info");
        break;
      default:
        this.iconPath = new vscode.ThemeIcon("question");
    }
  }
}