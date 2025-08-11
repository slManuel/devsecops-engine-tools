import * as vscode from "vscode";
import { DevSecOpsTreeDataProvider } from "../tree/DevSecOpsTreeDataProvider";
import { imageScanRequest } from "../application/InitEngineCore";
import { Docker, IOptions } from "docker-cli-js";
import { ScanConfiguration } from "../domain/model/ScanConfiguration";
import DockerPathDetector from "../infraestructure/helper/DockerPathDetector";
import { ScanOutputLoader } from "../infraestructure/helper/LoadingAnimator";

export function registerImageScanCommand(
  context: vscode.ExtensionContext,
  treeDataProvider: DevSecOpsTreeDataProvider
): vscode.Disposable {
  const imageScanDisposable = vscode.commands.registerCommand(
    "devsecops.imageScan",
    async () => {
      const images = await getDockerImages();
      let imageName = "";
      const quickPickItems: vscode.QuickPickItem[] = images.map((i) => {
        return {
          label: i.label?.toString() ?? "",
        };
      });

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

      // Start the loading animation
      const scanLoader = new ScanOutputLoader(outputChannel);
      scanLoader.start(`Docker Image: ${imageName}`);

      try {
        const scanResult = await scanner.makeScan(
          imageName,
          outputChannel,
          new ScanConfiguration()
        );

        if (scanResult) {
          // Stop animation and show completion - THIS PRESERVES ALL OUTPUT DATA
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

const getDockerImages = async (): Promise<vscode.TreeItem[]> => {
  const dockerPath = DockerPathDetector.getDockerPath();
  const options: IOptions = {
    env: {
      ...process.env,
      PATH: process.env.PATH + dockerPath.replace(/\/(docker|podman)$/, ""),
    },
  };
  const dockerCli = new Docker(options);

  const isDockerInstalled = await isInstalledDocker();

  if (!isDockerInstalled) {
    void vscode.window.showErrorMessage(
      "Docker is not installed or not found in the PATH."
    );
    return [];
  }

  return dockerCli
    .command("images")
    .then(function (data: { raw?: string }) {
      const output: string[] = typeof data.raw === "string" ? data.raw.split("\n") : [];
      const images: vscode.TreeItem[] = [];

      for (let i = 1; i < output.length; i++) {
        const line = output[i];
        if (typeof line !== "string") {
          continue;
        }
        const imageInfo: string[] = line.split(/\s+/);
        const imageName = imageInfo[0];
        const imageTag = imageInfo[1];

        if (imageName && imageTag) {
          const imageLabel = `${imageName}:${imageTag}`;
          const imageItem = new vscode.TreeItem(
            imageLabel,
            vscode.TreeItemCollapsibleState.None
          );
          imageItem.command = {
            command: "devsecops.imageScan",
            title: "Image Scan",
            arguments: [imageItem],
          };
          images.push(imageItem);
        }
      }

      return images;
    })
    .catch(function (err) {
      console.error(err);
      return [];
    });
};

const isInstalledDocker = async (): Promise<string | boolean> => {
  const dockerPath = DockerPathDetector.getDockerPath();
  const options: IOptions = {
    env: {
      ...process.env,
      PATH: process.env.PATH + dockerPath.replace(/\/(docker|podman)$/, ""),
    },
  };

  const dockerCli = new Docker(options);
  return dockerCli
    .command("version")
    .then(function (data: { raw?: string }) {
      const output = typeof data.raw === "string" ? data.raw.split("\n") : [];
      const version = output[1]?.split(":")[1]?.trim() ?? "";
      return version;
    })
    .catch(function (err) {
      console.error(err);
      return false;
    });
};
