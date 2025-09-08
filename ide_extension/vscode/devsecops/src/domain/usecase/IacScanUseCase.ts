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
import { ScannerRes } from "../model/ScannerRes";
import { ScanConfiguration } from "../model/ScanConfiguration";
import { Finding } from "../model/Finding";

interface IVariableData {
  value: string;
}

interface IReleaseIdData {
  variables: { [key: string]: IVariableData };
  environments: { variableGroups: number[] }[];
}

interface IVariableGroupData {
  value: { variables: { [key: string]: IVariableData } }[];
}

export class IacScanUseCase implements IIacScanUseCase {
  private files: string[] = [];

  constructor(
    private iacScanner: IacScanner,
    private restClient: IRestClientGateway,
    private toolVersion: string,
    private containerEnginePath: string
  ) { }

  public async scan(
    folderToScan: string,
    outputChannel: OutputChannel,
    scanConfiguration: ScanConfiguration,
    scanLoader: any
  ): Promise<ScannerRes> {
    let releaseIdData: IReleaseIdData;
    let variablesFromLibrary: { [key: string]: IVariableData } = {};
    let releaseEnvironments: number[] = [];
    let variableGroupsIds: number[] = [];
    let variableGroupsData: IVariableGroupData;
    let variableReplace: boolean = false;

    if (!scanConfiguration.isValidAdReplace()) {
      outputChannel.appendLine("Configuration values are missing≤ avoiding variable replace");
    } else {
      variableReplace = true;
      releaseIdData = (await this.restClient.get(
        VARIABLE_GROUPS_AD_BY_RELEASE_DEFINITION_ID.replace(
          "{organization}",
          scanConfiguration.getOrganizationName()
        )
          .replace("{project}", scanConfiguration.getProjectName())
          .replace("{definitionId}", scanConfiguration.getDefinitionId()),
        AuthEncoder.encode(
          scanConfiguration.getAdUserName(),
          scanConfiguration.getAdPersonalAccessToken()
        )
      )) as IReleaseIdData;
      variablesFromLibrary = releaseIdData.variables;
      releaseEnvironments = releaseIdData.environments
        .map((environment: { variableGroups: number[] }) => environment.variableGroups)
        .flat();
      variableGroupsIds = [...new Set(releaseEnvironments)];
      variableGroupsData = (await this.restClient.get(
        VARIABLE_GROUPS_AD_BY_ID.replace("{organization}", scanConfiguration.getOrganizationName())
          .replace("{project}", scanConfiguration.getProjectName())
          .replace("{groupIds}", variableGroupsIds.join(",")),
        AuthEncoder.encode(
          scanConfiguration.getAdUserName(),
          scanConfiguration.getAdPersonalAccessToken()
        )
      )) as IVariableGroupData;
      variableGroupsData.value.forEach(
        (variableGroup: { variables: { [x: string]: IVariableData } }) => {
          Object.keys(variableGroup.variables).forEach((variableName: string) => {
            variablesFromLibrary[variableName] = variableGroup.variables[variableName];
          });
        }
      );
    }

    this.files = await fs.readdir(folderToScan);
    const regex = /#{|}#/g;
    let replacedFile: string = "";


    const replacedFilesDir = path.join(folderToScan, 'replacedFiles');
    try {
      await fs.mkdir(replacedFilesDir, { recursive: true });
    } catch (error) {
      outputChannel.append(`Error creating replacedFiles directory: ${error}\n`);
    }

    while (this.files.length > 0 && variableReplace) {
      const file = this.files[0];
      replacedFile = "";

      const filePath = path.join(folderToScan, file);
      const fileStats = await fs.stat(filePath);
      if (fileStats.isDirectory()) {
        this.files = this.files.filter((value) => value !== file);
        continue;
      }
      const fileContent = await fs.readFile(filePath, "utf-8");
      const lines = fileContent.split("\n");
      replacedFile = this.processVariablesInLines(
        lines, regex, variablesFromLibrary, variableReplace, file, outputChannel
      );
      const newFilePath = path.join(replacedFilesDir, file);
      await fs.writeFile(newFilePath, replacedFile, "utf-8");
      this.files = this.files.filter((value) => value !== file);
    }


    const scanLocation = variableReplace ? path.join(folderToScan, 'replacedFiles') : folderToScan;
    
    const scannerRes: ScannerRes = await this.iacScanner.scan(
      scanLocation,
      outputChannel,
      scanConfiguration.getContainerImageName(),
      scanConfiguration.getIacTool(),
      this.toolVersion,
      this.containerEnginePath,
      scanLoader
    ).finally( () => {
      if(variableReplace) {
        this.cleanFolder(folderToScan);
      }
    });

    const findingsWithRuleCode: Finding[] = scannerRes.getFindings().map((finding: Finding) => {
      return this.iacScanner.getRuleCode(
        this.containerEnginePath,
        scanConfiguration.getContainerImageName(),
        this.toolVersion,
        finding.getId(),
        finding
      );
    });
    scannerRes.setFindings(await Promise.all(findingsWithRuleCode));
    return scannerRes;
  }

  private async cleanFolder(folderToScan: string): Promise<void> {
    const replacedFilesDir = path.join(folderToScan, 'replacedFiles');
    
    try {
      const stats = await fs.stat(replacedFilesDir);
      
      if (stats.isDirectory()) {
        const files = await fs.readdir(replacedFilesDir);
        
        for (const file of files) {
          const filePath = path.join(replacedFilesDir, file);
          const fileStats = await fs.stat(filePath);
          
          if (fileStats.isFile()) {
            await fs.unlink(filePath);
          } else if (fileStats.isDirectory()) {
            await this.cleanFolder(filePath);
          }
        }
        
        await fs.rmdir(replacedFilesDir);
      }
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
        console.error(`Error cleaning replacedFiles directory: ${error}`);
      }
    }
  }

  private processVariablesInLines(
    lines: string[], 
    regex: RegExp, 
    variablesFromLibrary: { [key: string]: IVariableData }, 
    variableReplace: boolean, 
    file: string, 
    outputChannel: OutputChannel
  ): string {
    let replacedFile = "";
    
    lines.forEach((line, _) => {
      if (regex.test(line)) {
        const variableName = line.split("#{")[1].split("}#")[0];
        if (variablesFromLibrary[variableName] && variableReplace) {
          replacedFile =
            replacedFile +
            "\n" +
            line.replace(`#{${variableName}}#`, variablesFromLibrary[variableName].value);
          outputChannel.append(`✅ Variable ${variableName} replaced in file ${file}\n`);
        } else {
          outputChannel.append(`⚠️ Variable ${variableName} not found in library for file ${file}\n`);
        }
      } else {
        replacedFile = replacedFile + "\n" + line;
      }
    });
    
    return replacedFile;
  }

}
