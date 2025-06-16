import * as vscode from 'vscode';
import { findingDetailWebview } from './FindingDetail';
import { Finding } from "../../../domain/model/Finding";

let vulnPanel: vscode.WebviewPanel | undefined;
let editorListener: vscode.Disposable | undefined;
let workspaceListener: vscode.Disposable | undefined;

export function showVulnContextWebview(finding: Finding): void {

    if (vulnPanel) {
        vulnPanel.webview.html = findingDetailWebview(finding);
        vulnPanel.reveal(vscode.ViewColumn.Beside);
    } else {
        vulnPanel = vscode.window.createWebviewPanel(
            'vulnContext',
            `Vulnerability: ${finding.getId()}`,
            vscode.ViewColumn.Beside,
            { enableScripts: true }
        );
         vulnPanel.webview.html = findingDetailWebview(finding);

        vulnPanel.onDidDispose(() => {
            disposeVulnPanel();
        });

        // Listen for editor changes and close the webview if no editors are open
        editorListener = vscode.window.onDidChangeVisibleTextEditors(editors => {
            if (editors.length === 0 && vulnPanel) {
                vulnPanel.dispose();
            }
        });

        // Listen for workspace changes and close the webview
        workspaceListener = vscode.workspace.onDidChangeWorkspaceFolders(() => {
            if (vulnPanel) {
                vulnPanel.dispose();
            }
        });
    }
}

export function disposeVulnPanel(): void {
    [vulnPanel, editorListener, workspaceListener].forEach(listener => {
        listener?.dispose?.();
    });
    vulnPanel = undefined;
    editorListener = undefined;
    workspaceListener = undefined;
}

