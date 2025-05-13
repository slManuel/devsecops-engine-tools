import { OutputChannel } from "vscode";
import { IIacScanUseCase } from "./interfaces/IIacScanUseCase";
import { IacScanner } from "../../infraestructure/drivenAdapter/IacScanner";
import { IRestClientGateway } from "../model/gateways/IRestClientGateway";
import {
  VARIABLE_GROUPS_AD_BY_RELEASE_DEFINITION_ID,
  VARIABLE_GROUPS_AD_BY_ID,
} from "../../application/appService/Constants";
import { AuthEncoder } from "../../infraestructure/helper/AuthEncoder";
import { promises as fs } from "fs";
import * as path from "path";

interface VariableData {
  value: string;
}

export class IacScanUseCase implements IIacScanUseCase {
  private files: string[] = [];

  constructor(
    private iacScanner: IacScanner,
    private restClient: IRestClientGateway,
    private toolVersion: string
  ) {}

  public async scan(
    folderToScan: string,
    dockerImageName: string,
    organizationName: string,
    projectName: string,
    definitionId: string,
    adUserName: string,
    adPersonalAccessToken: string,
    environment: string,
    outputChannel: OutputChannel
  ): Promise<boolean> {
    let releaseIdData: any;
    let variablesFromLibrary: { [key: string]: VariableData } = {};
    let releaseEnvironments: number[] = [];
    let variableGroupsIds: number[] = [];
    let variableGroupsData: any;
    let variableReplace: boolean = false;

    if (
      organizationName === "" ||
      projectName === "" ||
      definitionId === "" ||
      adUserName === "" ||
      adPersonalAccessToken === ""
    ) {
      console.log(
        "Configuration values are missing≤ avoiding variable replace"
      );
    } else {
      variableReplace = true;
      releaseIdData = await this.restClient.get(
        VARIABLE_GROUPS_AD_BY_RELEASE_DEFINITION_ID.replace(
          "{organization}",
          organizationName
        )
          .replace("{project}", projectName)
          .replace("{definitionId}", definitionId),
        AuthEncoder.encode(adUserName, adPersonalAccessToken)
      );
      variablesFromLibrary = releaseIdData.variables;
      releaseEnvironments = releaseIdData.environments.map(
        (environment: { variableGroups: number[] }) => {
          return environment.variableGroups;
        }
      );
      releaseEnvironments.push(releaseIdData.variableGroups);
      variableGroupsIds = [...new Set(releaseEnvironments.flat())];
      variableGroupsData = await this.restClient.get(
        VARIABLE_GROUPS_AD_BY_ID.replace("{organization}", organizationName)
          .replace("{project}", projectName)
          .replace("{groupIds}", variableGroupsIds.join(",")),
        AuthEncoder.encode(adUserName, adPersonalAccessToken)
      );
      variableGroupsData.value.forEach(
        (variableGroup: { variables: { [x: string]: VariableData } }) => {
          Object.keys(variableGroup.variables).forEach(
            (variableName: string) => {
              variablesFromLibrary[variableName] =
                variableGroup.variables[variableName];
            }
          );
        }
      );
    }

    this.files = await fs.readdir(folderToScan);
    const regex = /#{|}#/g;
    let replacedFile: string = "";

    let i = 0;
    while (this.files.length > 0) {
      const file = this.files[0];
      replacedFile = "";

      const filePath = path.join(folderToScan, file);
      const fileStats = await fs.stat(filePath);
      if (fileStats.isDirectory()) {
        continue;
      }
      const fileContent = await fs.readFile(filePath, "utf-8");
      const lines = fileContent.split("\n");
      lines.forEach((line, _) => {
        if (regex.test(line)) {
          const variableName = line.split("#{")[1].split("}#")[0];
          if (variablesFromLibrary[variableName] && variableReplace) {
            replacedFile =
              replacedFile +
              "\n" +
              line.replace(
                `#{${variableName}}#`,
                variablesFromLibrary[variableName].value
              );
          }
        } else {
          replacedFile = replacedFile + "\n" + line;
        }
      });
      const newFilePath = path.join(folderToScan, `modified_${file}`);
      await fs.writeFile(newFilePath, replacedFile, "utf-8");
      this.files = this.files.filter((value) => value !== file);
      i++;
    }
    await this.cleanFolder(folderToScan);
    return await this.iacScanner.scan(
      folderToScan,
      outputChannel,
      dockerImageName,
      this.toolVersion
    );
  }

  private async cleanFolder(folderToScan: string): Promise<void> {
    const files = await fs.readdir(folderToScan);
    for (const file of files) {
      if (file.startsWith("modified_")) {
        const filePath = path.join(folderToScan, file);
        const fileStats = await fs.stat(filePath);
        if (fileStats.isFile()) {
          await fs.unlink(filePath);
        }
      }
    }
  }
}
