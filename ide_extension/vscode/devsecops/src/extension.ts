import * as vscode from "vscode";
import { DiagnosticService } from "./tree/DiagnosticService";
import { DevSecOpsTreeDataProvider } from "./tree/DevSecOpsTreeDataProvider";
import { registerIacScanCommand } from "./commands/IacScanCommand";
import { Finding } from "./domain/model/Finding";
import { SecurityCodeActionProvider } from "./actions/SecurityCodeActionProvider";
import { registerImageScanCommand } from "./commands/ImageScanCommand";
import { registerDependenciesScanCommand } from "./commands/DependenciesScanCommand";
import { registerCopilotCommands } from "./commands/copilotCommands";
import { registerVulnerabilityCopilotCommands } from "./commands/vulnerabilityCopilotCommands";
import { showVulnContextWebview, disposeVulnPanel, showGeneralFindingWebview } from './tree/results/finding/FindingWebview';

export function activate(context: vscode.ExtensionContext): void {

  DiagnosticService.initialize();

  const treeDataProvider = new DevSecOpsTreeDataProvider(context);
  vscode.window.registerTreeDataProvider("devsecops", treeDataProvider);
  vscode.window.createTreeView("devsecops", {
    treeDataProvider: treeDataProvider,
    showCollapseAll: false,
    canSelectMany: false,
  });

  const iacScanDisposable = registerIacScanCommand(context, treeDataProvider);
  const imageScanDisposable = registerImageScanCommand(context, treeDataProvider);
  const dependenciesScanDisposable = registerDependenciesScanCommand(context, treeDataProvider);

  const codeActionProvider = vscode.languages.registerCodeActionsProvider(
    { scheme: 'file' },
    new SecurityCodeActionProvider(),
    {
      providedCodeActionKinds: SecurityCodeActionProvider.providedCodeActionKinds
    }
  );

  registerCopilotCommands(context);
  registerVulnerabilityCopilotCommands(context);

  const openWithDiagnosticDisposable = vscode.commands.registerCommand(
    "devsecops.openWithDiagnostic",
    (finding: Finding, filePath: string, lineNumberStart: number, _lineNumberEnd: number) => {
      DiagnosticService.showFindingInFile(finding, filePath, lineNumberStart);
    }
  );

  const showVulnContextDisposable = vscode.commands.registerCommand(
    "devsecops.showVulnContext",
    (finding: Finding) => {
      showVulnContextWebview(finding);
    }
  );

  const showGeneralFindingWebviewDisposable = vscode.commands.registerCommand(
    "devsecops.showGeneralFindingWebview",
    (findingItem: any) => {
      const finding = findingItem.finding ?? findingItem;
      showGeneralFindingWebview(finding);
    }
  );

  const deleteScanResultDisposable = vscode.commands.registerCommand(
    "devsecops.deleteScanResult",
    async (scanResultItem: any) => {
      const result = await vscode.window.showWarningMessage(
        `Are you sure you want to delete the scan result "${scanResultItem.label}"?`,
        { modal: true },
        "Delete",
        "Cancel"
      );

      if (result === "Delete") {
        treeDataProvider.deleteScanResult(scanResultItem);
        vscode.window.showInformationMessage(`Scan result "${scanResultItem.label}" has been deleted.`);
      }
    }
  );
  context.subscriptions.push(iacScanDisposable);
  context.subscriptions.push(imageScanDisposable);
  context.subscriptions.push(dependenciesScanDisposable);
  context.subscriptions.push(openWithDiagnosticDisposable);
  context.subscriptions.push(codeActionProvider);
  context.subscriptions.push(showVulnContextDisposable);
  context.subscriptions.push(showGeneralFindingWebviewDisposable);
  context.subscriptions.push(deleteScanResultDisposable);


  context.subscriptions.push({
    dispose: () => {
      DiagnosticService.dispose();
    }
  });
}

export function deactivate(): void {
  disposeVulnPanel();
  DiagnosticService.dispose();
}