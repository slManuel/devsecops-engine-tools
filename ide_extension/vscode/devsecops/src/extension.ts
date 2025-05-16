import * as vscode from "vscode";
import { DiagnosticService } from "./tree/DiagnosticService";
import { DevSecOpsTreeDataProvider } from "./tree/DevSecOpsTreeDataProvider";
import { registerIacScanCommand } from "./commands/IacScanCommand";
import { Finding } from "./domain/model/Finding";
import { SecurityCodeActionProvider } from "./actions/SecurityCodeActionProvider";
import { registerImageScanCommand } from "./commands/ImageScanCommand";
import { registerCopilotCommands } from "./commands/copilotCommands";


export function activate(context: vscode.ExtensionContext) {

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
  
  const codeActionProvider = vscode.languages.registerCodeActionsProvider(
    { scheme: 'file' },
    new SecurityCodeActionProvider(),
    {
      providedCodeActionKinds: SecurityCodeActionProvider.providedCodeActionKinds
    }
  );
  
  registerCopilotCommands(context);
  
  const openWithDiagnosticDisposable = vscode.commands.registerCommand(
    "devsecops.openWithDiagnostic", 
    (finding: Finding, filePath: string, lineNumberStart: number, lineNumberEnd: number) => {
      DiagnosticService.showFindingInFile(finding, filePath, lineNumberStart);
    }
  );
  
  context.subscriptions.push(iacScanDisposable);
  context.subscriptions.push(imageScanDisposable);
  context.subscriptions.push(openWithDiagnosticDisposable);
  context.subscriptions.push(codeActionProvider);
  
  context.subscriptions.push({
    dispose: () => {
      DiagnosticService.dispose();
    }
  });
}

export function deactivate() {
  DiagnosticService.dispose();
}