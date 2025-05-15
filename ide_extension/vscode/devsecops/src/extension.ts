import * as vscode from "vscode";
import { DevSecOpsTreeDataProvider } from "./tree/DevSecOpsTreeDataProvider";
import { registerIacScanCommand } from "./commands/IacScanCommand";
import { registerImageScanCommand } from "./commands/ImageScanCommand";

export function activate(context: vscode.ExtensionContext) {
  const treeDataProvider = new DevSecOpsTreeDataProvider(context);
  vscode.window.registerTreeDataProvider("devsecops", treeDataProvider);
  vscode.window.createTreeView("devsecops", {
    treeDataProvider: treeDataProvider,
    showCollapseAll: false,
    canSelectMany: false,
  });

  const iacScanDisposable = registerIacScanCommand(context, treeDataProvider);
  const imageScanDisposable = registerImageScanCommand(context, treeDataProvider);
  
  context.subscriptions.push(iacScanDisposable);
  context.subscriptions.push(imageScanDisposable);
}

export function deactivate() {}
