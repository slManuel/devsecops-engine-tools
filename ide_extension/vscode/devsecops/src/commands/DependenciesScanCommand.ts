import * as vscode from "vscode";
import * as path from "path";
import * as os from "os";
import { ResultsTreeDataProvider } from "../tree/ResultsTreeDataProvider";
import { dependenciesScanRequest } from "../application/InitEngineCore";
import { ScanConfiguration } from "../domain/model/ScanConfiguration";
import { ScanOutputLoader } from "../infrastructure/helper/LoadingAnimator";

export function registerDependenciesScanCommand(
    context: vscode.ExtensionContext,
    treeDataProvider: ResultsTreeDataProvider
): vscode.Disposable {
    const dependenciesScanDisposable = vscode.commands.registerCommand("devsecops.dependenciesScan", async () => {
        const selectedFolder = await vscode.window.showOpenDialog({
            canSelectFolders: true,
            canSelectFiles: false,
            canSelectMany: false,
            defaultUri:
                vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0
                    ? vscode.Uri.file(path.join(vscode.workspace.workspaceFolders[0].uri.fsPath, ""))
                    : vscode.Uri.file(os.homedir()),
            openLabel: "Select Folder",
        });

        if (selectedFolder && selectedFolder.length > 0) {
            let folderPath = selectedFolder[0].fsPath;
            folderPath = folderPath.replace(/^file:\/\//, "");

            void vscode.window.showInformationMessage(`DevSecOps Dependencies Scanning: ${folderPath}`);

            const useCase = await dependenciesScanRequest();
            const outputChannel = vscode.window.createOutputChannel("Dependencies Scan Results");
            outputChannel.clear();

            const scanLoader = new ScanOutputLoader(outputChannel);

            // Add loading placeholder
            const scanId = treeDataProvider.addLoadingScanResult(
                `Dependencies: ${folderPath.split('/').pop() || 'folder'}`,
                "dependencies",
                outputChannel
            );

            try {
                const scanResult = await useCase.scan(folderPath, outputChannel, new ScanConfiguration(), scanLoader);

                if (scanResult) {
                    scanLoader.stop(scanResult.getFindings().length, "dependency");

                    const severityCounts = scanResult.getSeverityCounts();
                    let message = "Dependencies Scan completed successfully";
                    
                    void vscode.window.showInformationMessage(message);
                    
                    // Update the loading placeholder with actual results
                    treeDataProvider.updateScanResult(
                        scanId,
                        scanResult.getFindings(),
                        "dependencies",
                        folderPath
                    );
                } else {
                    scanLoader.showError("Dependencies Scan failed - No results returned");
                    void vscode.window.showErrorMessage("Dependencies Scan failed");
                    // Remove the loading placeholder
                    treeDataProvider.removeScanResult(scanId);
                }
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
                scanLoader.showError(`Dependencies Scan failed: ${errorMessage}`);
                void vscode.window.showErrorMessage("Dependencies Scan failed");
                // Remove the loading placeholder
                treeDataProvider.removeScanResult(scanId);
            }
        }
    }
    );

    return dependenciesScanDisposable;
}