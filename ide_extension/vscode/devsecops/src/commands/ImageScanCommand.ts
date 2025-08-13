import * as vscode from "vscode";
import { DevSecOpsTreeDataProvider } from "../tree/DevSecOpsTreeDataProvider";
import { imageScanRequest } from "../application/InitEngineCore";
import { ScanConfiguration } from "../domain/model/ScanConfiguration";
import { ScanOutputLoader } from "../infraestructure/helper/LoadingAnimator";
import ContainerEngineManager from "../infraestructure/helper/ContainerEngineManager";

export function registerImageScanCommand(
  context: vscode.ExtensionContext,
  treeDataProvider: DevSecOpsTreeDataProvider
): vscode.Disposable {
  const imageScanDisposable = vscode.commands.registerCommand(
    "devsecops.imageScan",
    async () => {
      const images = await getContainerImages();
      let imageName = "";
      const quickPickItems: vscode.QuickPickItem[] = images.map((image) => {
        return {
          label: image.fullName
        };
      });

      if (quickPickItems.length === 0) {
        void vscode.window.showErrorMessage("No container images found. Please ensure you have images available in your container engine.");
        return;
      }

      const pickedImage = await vscode.window.showQuickPick(quickPickItems, {
        placeHolder: "Select an image to scan",
      });

      if (!pickedImage) {
        void vscode.window.showErrorMessage("No image selected");
        return;
      } else {
        imageName = pickedImage.label;
      }

      void vscode.window.showInformationMessage(
        `DevSecOps Image Scanning: ${imageName}`
      );

      const scanner = await imageScanRequest();
      const outputChannel = vscode.window.createOutputChannel("Image Scan Results");

      const scanLoader = new ScanOutputLoader(outputChannel);
      scanLoader.start(`Image: ${imageName}`);

      try {
        const scanResult = await scanner.makeScan(
          imageName,
          outputChannel,
          new ScanConfiguration()
        );

        if (scanResult) {
          scanLoader.stop(scanResult.getFindings().length, "image vulnerability");

          void vscode.window.showInformationMessage(
            "Image Scan completed successfully"
          );
          treeDataProvider.addScanResult(
            "IMAGE SCAN RESULT",
            scanResult.getFindings(),
            "image"
          );
        } else {
          scanLoader.showError("Image Scan failed - No results returned");
          void vscode.window.showErrorMessage("Image Scan failed");
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
        scanLoader.showError(`Image Scan failed: ${errorMessage}`);
        void vscode.window.showErrorMessage("Image Scan failed");
      }
    }
  );
  return imageScanDisposable;
}

const getContainerImages = async (): Promise<Array<{name: string, tag: string, fullName: string}>> => {
  const engineStatus = await ContainerEngineManager.isContainerEngineAvailable();

  if (!engineStatus.available) {
    const engineType = ContainerEngineManager.getEngineType();
    void vscode.window.showErrorMessage(
      `${engineType.charAt(0).toUpperCase() + engineType.slice(1)} is not installed or not found in the PATH.`
    );
    return [];
  }

  try {
    const images = await ContainerEngineManager.getContainerImages();
    return images;
  } catch (error) {
    console.error("Error getting container images:", error);
    void vscode.window.showErrorMessage(
      `Error retrieving container images: ${error instanceof Error ? error.message : String(error)}`
    );
    return [];
  }
};
