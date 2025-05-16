import * as vscode from "vscode";
import * as path from "path";
import { Finding } from "../../../domain/model/Finding";

export class FindingItem extends vscode.TreeItem {
  constructor(
    public readonly finding: Finding,
    private readonly scanPath?: string
  ) {
    super(finding.getDescription() || "Unknown Issue", vscode.TreeItemCollapsibleState.None);
    this.label = finding.getId() || "Unknown Issue";
    this.description = finding.getSeverity() || "Unknown";
    this.tooltip = `${finding.getDescription()}\nSeverity: ${finding.getSeverity()}\nResource: ${finding.getResource() || "Unknown"}\nLocation: ${finding.getWhere() || "Unknown"}`;
    
    const severityIcons: Record<string, vscode.ThemeIcon> = {
      "high": new vscode.ThemeIcon("error", new vscode.ThemeColor("errorForeground")),
      "medium": new vscode.ThemeIcon("warning", new vscode.ThemeColor("editorWarning.foreground")),
      "low": new vscode.ThemeIcon("info", new vscode.ThemeColor("editorInfo.foreground")),
    };
    
    this.iconPath = severityIcons[finding.getSeverity().toLowerCase()] || 
      new vscode.ThemeIcon("error", new vscode.ThemeColor("errorForeground"));
    
    const fileInfo = this.extractFileInfo(finding.getWhere());
    
    if (fileInfo.filePath) {
      // Use the new command instead of directly opening the file
      this.command = {
        title: "Open File",
        command: "devsecops.openWithDiagnostic",
        arguments: [
          finding,
          fileInfo.filePath,
          fileInfo.lineNumber || 1
        ]
      };
    }
  }
  private extractFileInfo(where: string): { filePath: string | null; lineNumber: number | null } {
    if (!where) {
      return { filePath: null, lineNumber: null };
    }
    
    // Try to extract line number
    const lineMatch = where.match(/\(line\s+(\d+)\)/);
    const lineNumber = lineMatch ? parseInt(lineMatch[1], 10) : null;
    
    let filePath: string | null = null;
    
    const pathMatch = where.match(/\/ms_artifact(\/.+?)(?::|$|\s)/);
    if (pathMatch && pathMatch[1] && this.scanPath) {
      filePath = path.join(this.scanPath, pathMatch[1].substring(1));
    } else {
      const genericPathMatch = where.match(/\/([\/\w\.-]+)(?::|$|\s)/);
      if (genericPathMatch && this.scanPath) {
        filePath = path.join(this.scanPath, genericPathMatch[1]);
      }
    }
    
    return { filePath, lineNumber };
  }
}