import * as vscode from "vscode";
import { Finding } from "../domain/model/Finding";

export class DiagnosticService {
  private static diagnosticCollection: vscode.DiagnosticCollection | undefined;
  private static findingMap: Map<string, Finding> = new Map();

  public static initialize() {
    if (!this.diagnosticCollection) {
      this.diagnosticCollection = vscode.languages.createDiagnosticCollection("devsecops");
    }
  }

  public static showFindingInFile(finding: Finding, filePath: string, lineNumber: number) {
    this.initialize();
    
    const fileUri = vscode.Uri.file(filePath);
    
    const diagnostic = new vscode.Diagnostic(
      new vscode.Range(
        new vscode.Position(lineNumber - 1, 0),
        new vscode.Position(lineNumber - 1, 100)
      ),
      finding.getDescription(),
      this.getSeverity(finding.getSeverity())
    );
    
    diagnostic.source = "devsecops";
    diagnostic.code = finding.getId();
    
    const key = `${fileUri.toString()}:${finding.getId()}`;
    this.findingMap.set(key, finding);
    
    this.diagnosticCollection?.set(fileUri, [diagnostic]);
    
    vscode.window.showTextDocument(fileUri, {
      selection: new vscode.Range(lineNumber - 1, 0, lineNumber - 1, 0),
      preview: true
    });
  }

  public static getFindingForDiagnostic(fileUri: vscode.Uri, diagnosticCode: string): Finding | undefined {
    const key = `${fileUri.toString()}:${diagnosticCode}`;
    return this.findingMap.get(key);
  }

  private static getSeverity(severity: string): vscode.DiagnosticSeverity {
    return vscode.DiagnosticSeverity.Error;
  }

  public static clearDiagnostics() {
    this.diagnosticCollection?.clear();
    this.findingMap.clear();
  }

  public static dispose() {
    this.diagnosticCollection?.dispose();
    this.findingMap.clear();
  }
}