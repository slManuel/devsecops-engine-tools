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
    this.iconPath = new vscode.ThemeIcon("error");
  }
}