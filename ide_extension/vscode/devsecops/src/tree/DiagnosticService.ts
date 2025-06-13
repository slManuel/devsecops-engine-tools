import * as vscode from "vscode";
import { Finding } from "../domain/model/Finding";

export class DiagnosticService {
  private static diagnosticCollection: vscode.DiagnosticCollection | undefined;
  private static findingMap: Map<string, Finding> = new Map();

  public static initialize(): void {
    if (!this.diagnosticCollection) {
      this.diagnosticCollection = vscode.languages.createDiagnosticCollection("devsecops");
    }
  }

  public static showFindingInFile(finding: Finding, filePath: string, lineNumberStart: number, lineNumberEnd: number = lineNumberStart): void {
    this.initialize();
    
    const fileUri = vscode.Uri.file(filePath);
    
    const diagnostic = new vscode.Diagnostic(
      new vscode.Range(
        new vscode.Position(lineNumberStart - 1, 0),
        new vscode.Position(lineNumberEnd - 1, 100) // Assuming max line length of 100
      ),
      finding.getDescription() + finding.getValidationRuleCode() ? `\nValidation Rule: ${finding.getValidationRuleCode()}` : '',
      vscode.DiagnosticSeverity.Error
    );
    
    diagnostic.source = "devsecops";
    diagnostic.code = finding.getId();
    
    // Add validation rule information if available
    if (finding.getValidationRuleCode()) {
      diagnostic.relatedInformation = [
        new vscode.DiagnosticRelatedInformation(
          new vscode.Location(fileUri, diagnostic.range),
          `Validation Rule: ${finding.getValidationRuleCode()}`
        )
      ];
      
      // Also add validation rule as a tag for better organization
      diagnostic.tags = [vscode.DiagnosticTag.Unnecessary];
    }
    
    const key = `${fileUri.toString()}:${finding.getId()}`;
    this.findingMap.set(key, finding);
    
    this.diagnosticCollection?.set(fileUri, [diagnostic]);
    
    void vscode.window.showTextDocument(fileUri, {
      selection: new vscode.Range(lineNumberStart - 1, 0, lineNumberStart - 1, 0),
      preview: true
    });
  }

  public static getFindingForDiagnostic(fileUri: vscode.Uri, diagnosticCode: string): Finding | undefined {
    const key = `${fileUri.toString()}:${diagnosticCode}`;
    return this.findingMap.get(key);
  }

  public static getValidationRuleForDiagnostic(diagnostic: vscode.Diagnostic): string | undefined {
    if (diagnostic.source === 'devsecops' && diagnostic.relatedInformation?.length) {
      const relatedInfo = diagnostic.relatedInformation[0]?.message;
      if (relatedInfo?.startsWith('Validation Rule: ')) {
        return relatedInfo.replace('Validation Rule: ', '');
      }
    }
    return undefined;
  }

  public static clearDiagnostics(): void {
    this.diagnosticCollection?.clear();
    this.findingMap.clear();
  }

  public static dispose(): void {
    this.diagnosticCollection?.dispose();
    this.findingMap.clear();
  }
}