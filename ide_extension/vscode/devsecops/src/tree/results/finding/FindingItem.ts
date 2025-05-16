import * as vscode from "vscode";
import * as path from "path";
import { Finding } from "../../../domain/model/Finding";

export class FindingItem extends vscode.TreeItem {
  constructor(
    public readonly finding: Finding,
    private readonly scanPath?: string // Add optional parameter for original scan path
  ) {
    super(finding.getDescription() || "Unknown Issue", vscode.TreeItemCollapsibleState.None);
    this.label = finding.getId() || "Unknown Issue";
    this.description = finding.getSeverity() || "Unknown";
    this.tooltip = `${finding.getDescription()}\nSeverity: ${finding.getSeverity()}\nResource: ${finding.getResource() || "Unknown"}\nLocation: ${finding.getWhere() || "Unknown"}`;
    
    // Set icon based on severity
    const severityIcons: Record<string, vscode.ThemeIcon> = {
      "high": new vscode.ThemeIcon("error", new vscode.ThemeColor("errorForeground")),
      "medium": new vscode.ThemeIcon("warning", new vscode.ThemeColor("editorWarning.foreground")),
      "low": new vscode.ThemeIcon("info", new vscode.ThemeColor("editorInfo.foreground")),
    };
    
    this.iconPath = severityIcons[finding.getSeverity().toLowerCase()] || 
      new vscode.ThemeIcon("error", new vscode.ThemeColor("errorForeground"));
    
    // Extract file path and line number from the where property
    const fileInfo = this.extractFileInfo(finding.getWhere());
    
    if (fileInfo.filePath) {
      // Add command to open the file when clicked
      this.command = {
        title: "Open File",
        command: "vscode.open",
        arguments: [
          vscode.Uri.file(fileInfo.filePath),
          {
            preview: true,
            selection: fileInfo.lineNumber ? 
              new vscode.Range(fileInfo.lineNumber - 1, 0, fileInfo.lineNumber - 1, 0) : 
              undefined
          }
        ]
      };
    }
  }
  
  /**
   * Extracts file path and line number from the where property
   * Example input: "/ms_artifact/Dockerfile: /Dockerfile.FROM (line 1)"
   */
  private extractFileInfo(where: string): { filePath: string | null; lineNumber: number | null } {
    if (!where) {
      return { filePath: null, lineNumber: null };
    }
    
    // Try to extract line number
    const lineMatch = where.match(/\(line\s+(\d+)\)/);
    const lineNumber = lineMatch ? parseInt(lineMatch[1], 10) : null;
    
    // Try to extract file path - needs to be adjusted based on the actual format
    let filePath: string | null = null;
    
    // Remove "/ms_artifact" prefix which is the Docker mount point
    const pathMatch = where.match(/\/ms_artifact(\/.+?)(?::|$|\s)/);
    if (pathMatch && pathMatch[1] && this.scanPath) {
      // Convert the container path to the actual file path
      filePath = path.join(this.scanPath, pathMatch[1].substring(1));
    } else {
      // Try to find any path-like string
      const genericPathMatch = where.match(/\/([\/\w\.-]+)(?::|$|\s)/);
      if (genericPathMatch && this.scanPath) {
        filePath = path.join(this.scanPath, genericPathMatch[1]);
      }
    }
    
    return { filePath, lineNumber };
  }
}