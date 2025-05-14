import * as vscode from "vscode";
import { FindingItem } from "./finding/FindingItem";

export class ScanResultItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly description: string,
    public readonly timestamp: Date,
    public readonly children: vscode.TreeItem[]
  ) {
    super(label, vscode.TreeItemCollapsibleState.Collapsed);
    this.tooltip = `${label} - ${children.length} findings`;
    this.description = `${children.length} findings - ${timestamp.toLocaleString()}`;
    this.iconPath = children.length > 0 
      ? new vscode.ThemeIcon("warning") 
      : new vscode.ThemeIcon("pass");
  }
}