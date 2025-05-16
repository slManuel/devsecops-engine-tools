import * as vscode from "vscode";
import { DevSecOpsTreeDataProvider } from "../tree/DevSecOpsTreeDataProvider";
import { imageScanRequest } from "../application/InitEngineCore";
import { Docker, IOptions } from "docker-cli-js";
import { ScanConfiguration } from "../domain/model/ScanConfiguration";

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
        vscode.window.showErrorMessage("No image selected");
        return;
      } else {
        imageName = pickedImage.label;
      }

      vscode.window.showInformationMessage(
        `DevSecOps Image Scanning: ${imageName}`
      );

      const scanner = await imageScanRequest();
      const outputChannel =
        vscode.window.createOutputChannel("IaC Scan Results");

      let scanResult = await scanner.makeScan(
        imageName,
        outputChannel,
        new ScanConfiguration()
      );

      if (scanResult) {
        vscode.window.showInformationMessage(
          "Image Scan completed successfully"
        );
        treeDataProvider.addScanResult(
          "IMAGE SCAN RESULT",
          scanResult.getFindings(),
          "image",
          undefined
        );
      } else {
        vscode.window.showErrorMessage("Image Scan failed");
      }
    }
  );
  return imageScanDisposable;
}

const getDockerImages = async () => {
  const options: IOptions = {
    env: {
      ...process.env,
      PATH: process.env.PATH + ":/usr/local/bin",
    },
  };
  const dockerCli = new Docker(options);

  const isDockerInstalled = await isInstalledDocker();

  if (!isDockerInstalled) {
    vscode.window.showErrorMessage(
      "Docker is not installed or not found in the PATH."
    );
    return [];
  }

  return dockerCli
    .command("images")
    .then(function (data) {
      const output = data.raw.split("\n");
      const images = [];

      for (let i = 1; i < output.length; i++) {
        const imageInfo = output[i].split(/\s+/);
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

const isInstalledDocker = async () => {
  const options: IOptions = {
    env: {
      ...process.env,
      PATH: process.env.PATH + ":/usr/local/bin",
    },
  };

  const dockerCli = new Docker(options);
  return dockerCli
    .command("version")
    .then(function (data) {
      const output = data.raw.split("\n");
      const version = output[1].split(":")[1].trim();
      return version;
    })
    .catch(function (err) {
      console.error(err);
      return false;
    });
};
