import * as vscode from 'vscode';
import { findingDetailWebview } from './FindingDetail';
import { Finding } from "../../../domain/model/Finding";

let vulnPanel: vscode.WebviewPanel | undefined;
let editorListener: vscode.Disposable | undefined;
let workspaceListener: vscode.Disposable | undefined;
let messageListener: vscode.Disposable | undefined;

export function showVulnContextWebview(finding: Finding, sourceType?: string): void {

    if (vulnPanel) {
        vulnPanel.webview.html = findingDetailWebview(finding, sourceType);
        vulnPanel.title = `Vulnerability: ${finding.getId()}`;
        vulnPanel.reveal(vscode.ViewColumn.Beside);
        
        // Dispose the old message listener and create a new one with the current finding
        if (messageListener) {
            messageListener.dispose();
        }
        setupMessageHandler(vulnPanel, finding);
    } else {
        vulnPanel = vscode.window.createWebviewPanel(
            'vulnContext',
            `Vulnerability: ${finding.getId()}`,
            vscode.ViewColumn.Beside,
            { enableScripts: true }
        );
        vulnPanel.webview.html = findingDetailWebview(finding, sourceType);

        // Setup message handler for the current finding
        setupMessageHandler(vulnPanel, finding);

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

function setupMessageHandler(panel: vscode.WebviewPanel, finding: Finding): void {
    // Handle messages from the webview
    messageListener = panel.webview.onDidReceiveMessage(
        async (message) => {
            switch (message.command) {
                case 'fixWithCopilot':
                    await vscode.commands.executeCommand('devsecops.fixVulnerabilityWithCopilot', {
                        finding: finding,
                        sourceType: message.sourceType
                    });
                    break;
                case 'explainWithCopilot':
                    await vscode.commands.executeCommand('devsecops.explainVulnerabilityWithCopilot', {
                        finding: finding,
                        sourceType: message.sourceType
                    });
                    break;
                case 'generateDependencyUpdate':
                    await vscode.commands.executeCommand('devsecops.generateDependencyUpdate', {
                        finding: finding
                    });
                    break;
                case 'autoFixWithAgent':
                case 'autoFixDependenciesWithAgent':
                    await vscode.commands.executeCommand('devsecops.autoFixDependenciesWithAgent', {
                        finding: finding
                    });
                    break;
            }
        }
    );
}

export function disposeVulnPanel(): void {
    [vulnPanel, editorListener, workspaceListener, messageListener].forEach(listener => {
        listener?.dispose?.();
    });
    vulnPanel = undefined;
    editorListener = undefined;
    workspaceListener = undefined;
    messageListener = undefined;
}

