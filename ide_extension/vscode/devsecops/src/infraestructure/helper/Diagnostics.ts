import * as vscode from 'vscode';

const diagnosticCollection = vscode.languages.createDiagnosticCollection('iacVulnerabilities');

/**
 * Adds diagnostics (squiggles/underlines) to the specified lines in a file.
 * @param filePath The absolute path to the file
 * @param lines An array of zero-based line numbers to underline
 * @param message The message to show in the Problems panel and on hover
 */
export function setDiagnostics(filePath: string, lines: number[], message: string) {
    const uri = vscode.Uri.file(filePath);
    const diagnostics: vscode.Diagnostic[] = lines.map(line => {
        // Underline the whole line
        const range = new vscode.Range(line, 0, line, Number.MAX_SAFE_INTEGER);
        return new vscode.Diagnostic(range, message, vscode.DiagnosticSeverity.Warning);
    });
    diagnosticCollection.set(uri, diagnostics);
}

/**
 * Clears all diagnostics.
 */
export function clearDiagnostics() {
    diagnosticCollection.clear();
}