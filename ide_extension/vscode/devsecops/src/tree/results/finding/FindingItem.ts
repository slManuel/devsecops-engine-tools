import * as vscode from "vscode";
import { Finding } from "../../../domain/model/Finding";

export class FindingItem extends vscode.TreeItem {
  constructor(
    public readonly finding: Finding // Using any for now, replace with proper type from your ScannerRes
  ) {
    super(finding.getDescription() || "Unknown Issue", vscode.TreeItemCollapsibleState.None);
    this.label = finding.getId() || "Unknown Issue";
    this.description = finding.getSeverity() || "Unknown";
    this.tooltip = `${finding.getDescription()}\nSeverity: ${finding.getSeverity()}\nResource: ${finding.getResource() || "Unknown"}`;
    
    // Set icon based on severity
    switch (finding.getSeverity()?.toLowerCase()) {
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