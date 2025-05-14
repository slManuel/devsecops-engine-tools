import * as vscode from "vscode";
import * as path from "path";
import { iacScanRequest, imageScanRequest } from "./application/InitEngineCore";
import { Docker, IOptions } from "docker-cli-js";
import { DevSecOpsTreeDataProvider } from "./tree/DevSecOpsTreeDataProvider";

export function activate(context: vscode.ExtensionContext) {
  const treeDataProvider = new DevSecOpsTreeDataProvider(context);
  vscode.window.registerTreeDataProvider("devsecops", treeDataProvider);
  vscode.window.createTreeView("devsecops", {
    treeDataProvider: treeDataProvider,
    showCollapseAll: false,
    canSelectMany: false,
  });

  console.log("DevSecOpse IDE Extension active");

  const iacScanDisposable = vscode.commands.registerCommand(
    "devsecops.iacScan",
    async () => {
      const selectedFolder = await vscode.window.showOpenDialog({
        canSelectFolders: true,
        canSelectFiles: false,
        canSelectMany: false,
        defaultUri:
          vscode.workspace.workspaceFolders &&
          vscode.workspace.workspaceFolders.length > 0
            ? vscode.Uri.file(
                path.join(vscode.workspace.workspaceFolders[0].uri.fsPath, "")
              )
            : vscode.Uri.file(require("os").homedir()),
        openLabel: "Select Folder",
      });

      const dockerImageName: string =
        vscode.workspace.getConfiguration("devsecops").get("imageToUse") || "";
      const organizationName: string =
        vscode.workspace
          .getConfiguration("devsecops")
          .get("organizationName") || "";
      const projectName: string =
        vscode.workspace.getConfiguration("devsecops").get("projectName") || "";
      const definitionId: string =
        vscode.workspace.getConfiguration("devsecops").get("releaseId") || "";
      const environment: string =
        vscode.workspace.getConfiguration("devsecops").get("environment") || "";
      const adUserName: string =
        vscode.workspace.getConfiguration("devsecops").get("username") || "";
      const adPersonalAccessToken: string =
        vscode.workspace
          .getConfiguration("devsecops")
          .get("personalAccessToken") || "";

      if (selectedFolder && selectedFolder.length > 0) {
        let folderPath = selectedFolder[0].fsPath;

        folderPath = folderPath.replace(/^file:\/\//, "");

        vscode.window.showInformationMessage(
          `DevSecOps Iac Scanning: ${folderPath}`
        );

        const scanner = await iacScanRequest();
        const outputChannel =
          vscode.window.createOutputChannel("IaC Scan Results");
        let scanResult = await scanner.makeScan(
          folderPath,
          dockerImageName,
          organizationName,
          projectName,
          definitionId,
          adUserName,
          adPersonalAccessToken,
          environment,
          outputChannel
        );
        console.log("Scan result: ", scanResult);
        if (scanResult) {
          vscode.window.showInformationMessage(
            "Iac Scan completed successfully"
          );
          treeDataProvider.addScanResult(
            "IAC SCAN RESULT",
            scanResult.getFindings(),
            'iac'
          );
        } else {
          vscode.window.showErrorMessage("Iac Scan failed");
        }
      }
    }
  );

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

  const imageScanDisposable = vscode.commands.registerCommand(
    "devsecops.imageScan",
    async () => {
      const dockerImageName: string =
        vscode.workspace.getConfiguration("devsecops").get("imageToUse") || "";
      const images = await getDockerImages();
      let imageName = "";
      const imageOptions = images.map((image) => image.label);
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
        dockerImageName
      );

      if (scanResult) {
        vscode.window.showInformationMessage(
          "Image Scan completed successfully"
        );
      } else {
        vscode.window.showErrorMessage("Image Scan failed");
      }
    }
  );

  context.subscriptions.push(iacScanDisposable);
  context.subscriptions.push(imageScanDisposable);
}

// This method is called when your extension is deactivated
export function deactivate() {}
