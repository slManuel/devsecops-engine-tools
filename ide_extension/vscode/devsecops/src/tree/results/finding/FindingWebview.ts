import * as vscode from 'vscode';
import { findingDetailWebview } from './FindingDetail';
import { Finding } from "../../../domain/model/Finding";

let vulnPanels: Map<string, vscode.WebviewPanel> = new Map();

export function showVulnContextWebview(finding: Finding, sourceType?: string): void {
    const panelId = `vulnContext-${finding.getId()}-${new Date().getTime()}`;

    if (vulnPanels.has(panelId)) {
        const existingPanel = vulnPanels.get(panelId);
        existingPanel?.reveal(vscode.ViewColumn.Beside);
    } else {
        const vulnPanel = vscode.window.createWebviewPanel(
            'vulnContext',
            `Finding: ${finding.getId()}`,
            vscode.ViewColumn.Beside,
            { enableScripts: true, retainContextWhenHidden: true }
        );

        // Determine sourceType from finding module if not provided
        const actualSourceType = sourceType || getSourceTypeFromModule(finding.getModule());
        vulnPanel.webview.html = findingDetailWebview(finding, actualSourceType);

        // Setup message handler for Copilot buttons
        setupMessageHandler(vulnPanel, finding);

        vulnPanel.onDidDispose(() => {
            vulnPanels.delete(panelId);
        });

        vulnPanels.set(panelId, vulnPanel);
    }
}

function getSourceTypeFromModule(module: string): string {
    switch (module) {
        case 'engine_iac':
            return 'iac';
        case 'engine_container':
        case 'engine_image':
            return 'image';
        case 'engine_dependencies':
            return 'dependencies';
        case 'engine_secrets':
            return 'secrets';
        default:
            return 'unknown';
    }
}

function setupMessageHandler(panel: vscode.WebviewPanel, finding: Finding): void {
    // Handle messages from the webview
    panel.webview.onDidReceiveMessage(
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

// Generic alias for all practices
export const showGeneralFindingWebview = showVulnContextWebview;

export function disposeVulnPanel(): void {
    vulnPanels.forEach(panel => {
        panel.dispose();
    });
    vulnPanels.clear();
}

