import * as vscode from 'vscode';

let vulnPanel: vscode.WebviewPanel | undefined;
let editorListener: vscode.Disposable | undefined;
let workspaceListener: vscode.Disposable | undefined;

export function showVulnContextWebview(contextInfo: any) {

    if (vulnPanel) {
        vulnPanel.webview.html = getWebviewContent(contextInfo);
        vulnPanel.reveal(vscode.ViewColumn.Beside);
    } else {
        vulnPanel = vscode.window.createWebviewPanel(
            'vulnContext',
            `Vulnerability Context: ${contextInfo.id}`,
            vscode.ViewColumn.Beside,
            { enableScripts: true }
        );
        vulnPanel.webview.html = getWebviewContent(contextInfo);

        vulnPanel.onDidDispose(() => {
            vulnPanel = undefined;
            if (editorListener) {
                editorListener.dispose();
                editorListener = undefined;
            }
            if (workspaceListener) {
                workspaceListener.dispose();
                workspaceListener = undefined;
            }
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

export function disposeVulnPanel() {
    if (vulnPanel) {
        vulnPanel.dispose();
        vulnPanel = undefined;
    }
    if (editorListener) {
        editorListener.dispose();
        editorListener = undefined;
    }
    if (workspaceListener) {
        workspaceListener.dispose();
        workspaceListener = undefined;
    }
}

function getWebviewContent(contextInfo: any): string {

 const severity = (contextInfo.severity || "unknown").toLowerCase();
        let codicon = "codicon-warning";
    let color = "#cca700"; // yellow for medium/warning
    if (severity === "high") {
        codicon = "codicon-error";
        color = "#e51400"; // red for error
    }
    else if (severity === "critical") {
        codicon = "codicon-error";
        color = "#e51400"; // red for critical
    } else if (severity === "medium") {
        codicon = "codicon-warning";
        color = "#cca700"; // yellow for warning
    } else if (severity === "low") {
        codicon = "codicon-info";
        color = "#007acc"; // blue for info
    }
    

    function scanInfoRow(label: string, value: string | undefined) {
        return `<div class="scan-row"><span class="scan-label">${label}:</span> <span class="scan-value">${value || "-"}</span></div>`;
    }
    
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <link href="https://microsoft.github.io/vscode-codicons/dist/codicon.css" rel="stylesheet" />
        <style>
            body { font-family: sans-serif; padding: 1.5em; }
            .title-bar {
                display: flex;
                align-items: center;
                font-size: 1.5em;
                margin-bottom: 0.5em;
            }
            .codicon {
                font-size: 2em;
                margin-right: 0.5em;
                vertical-align: middle;
                color: ${color};
            }
           .vuln-underline {
                position: absolute;
                left: 0;
                bottom: -4px;
                width: 100%;
                height: 4px;
                background: ${color};
                border-radius: 2px;
                content: "";
            }
            .vuln-icon {
                font-size: 10rem; 
                color: ${color};
                margin-right: 0.5em;
                vertical-align: middle;
            } 
            .tabs {
                display: flex;
                margin-bottom: 1em;
            }
            .tab {
                padding: 0.5em 1.5em;
                cursor: pointer;
                border: none;
                background: none;
                font-size: 1em;
                outline: none;
                color: #fff;
                border-bottom: none;
                transition: background 0.2s;
            }
            .tab.selected {
                border-bottom: 3px solid #007acc;
                font-weight: bold;
            }
            .section {
                display: none;

            }
            .section.active {
                display: block;
            }
            .scan-row {
                margin: 0.4em 0;
            }
            .scan-label {
                font-weight: bold;
                color: #fff;
                min-width: 160px;
                display: inline-block;
            }
            .scan-value {
                color: #fff;
            }
        </style>
    </head>
    <body>
        <div class="title-bar">
            <span class="codicon ${codicon} vuln-icon"></span>
            <span>${contextInfo.id || "Unknown Vulnerability"}</span>
            <div class="vuln-underline"></div>
        </div>
        <div class="tabs">
            <button class="tab selected" id="descTab">Description</button>
            <button class="tab" id="scanTab">Scan Info</button>
            <button class="tab" id="remTab">Remediation Info</button>
        </div>
        <div class="section active" id="descSection">
            <h3>Description</h3>
            <p>${contextInfo.description || "No description available."}</p>
        </div>
        <div class="section" id="scanSection">
            <h3>Scan Info</h3>
            ${scanInfoRow("Severity", contextInfo.severity)}
            ${scanInfoRow("Vulnerability Status", contextInfo.vulnerability_status)}
            ${scanInfoRow("Installed Version", contextInfo.installed_version)}
            ${scanInfoRow("Fixed Version", contextInfo.fixed_version)}
            ${scanInfoRow("Target Image", contextInfo.target_image)}
            ${scanInfoRow("Package Name", contextInfo.package_name)}
            ${scanInfoRow("CVSS 3", contextInfo.cvss3)}
        </div>
        <div class="section" id="remSection">
            <h3>Remediation Info</h3>
            <p>${contextInfo.description || "No remediation info available."}</p>
            <pre>${JSON.stringify(contextInfo, null, 2)}</pre>
        </div>
        <script>
            const descTab = document.getElementById('descTab');
            const scanTab = document.getElementById('scanTab');
            const remTab = document.getElementById('remTab');
            const descSection = document.getElementById('descSection');
            const scanSection = document.getElementById('scanSection');
            const remSection = document.getElementById('remSection');
            function selectTab(tab, section) {
                [descTab, scanTab, remTab].forEach(t => t.classList.remove('selected'));
                [descSection, scanSection, remSection].forEach(s => s.classList.remove('active'));
                tab.classList.add('selected');
                section.classList.add('active');
            }
            descTab.onclick = () => selectTab(descTab, descSection);
            scanTab.onclick = () => selectTab(scanTab, scanSection);
            remTab.onclick = () => selectTab(remTab, remSection);
        </script>
    </body>
    </html>
    `;
}