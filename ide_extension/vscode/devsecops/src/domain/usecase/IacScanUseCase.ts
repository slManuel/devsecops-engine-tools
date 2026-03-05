import { OutputChannel } from "vscode";
import { IIacScanUseCase } from "./interfaces/IIacScanUseCase";
import { IacScanner } from "../../infrastructure/scanners/IacScanner";
import { IRestClientGateway } from "../model/gateways/IRestClientGateway";
import {
  VARIABLE_GROUPS_AD_BY_RELEASE_DEFINITION_ID,
  VARIABLE_GROUPS_AD_BY_ID,
} from "../../application/appService/Constants";
import { AuthEncoder } from "../../infrastructure/helper/AuthEncoder";
import { promises as fs } from "fs";
import * as path from "path";
import { ScannerRes } from "../model/ScannerRes";
import { ScanConfiguration } from "../model/ScanConfiguration";
import { Finding } from "../model/Finding";
import { ScanExecutionOrchestrator } from "../../infrastructure/executors/ScanExecutionOrchestrator";
import { IScanExecutionConfig } from "../../infrastructure/executors/IScanExecutor";
import { Mappers } from "../model/mappers/Mappers";

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
    // Select executor based on configuration
    const executor = await ScanExecutionOrchestrator.selectExecutor();
    await ScanExecutionOrchestrator.getExecutionModeStatus(outputChannel);

    // Check if we should use remote executor
    if (executor.getExecutionMode() === 'remote-microservice') {
      return await this.executeScanViaRemote(
        folderToScan,
        outputChannel,
        scanConfiguration,
        executor
      );
    }

    // Use local Docker execution (traditional flow)
    return await this.executeScanViaLocal(
      folderToScan,
      outputChannel,
      scanConfiguration,
      scanLoader
    );
  }

  private async executeScanViaRemote(
    folderToScan: string,
    outputChannel: OutputChannel,
    scanConfiguration: ScanConfiguration,
    executor: any
  ): Promise<ScannerRes> {
    // Show output channel
    outputChannel.show();
    
    // Process variable replacement if needed (same as local)
    const scanLocation = await this.prepareFilesForScan(folderToScan, outputChannel, scanConfiguration);

    try {
      // Build config for remote execution
      const scanConfig: IScanExecutionConfig = {
        scanType: 'iac',
        target: scanLocation,
        containerImageName: scanConfiguration.getContainerImageName(),
        toolVersion: this.toolVersion,
        iacTool: scanConfiguration.getIacTool()
      };

      // Execute via remote microservice
      const result = await executor.execute(scanConfig, outputChannel);

      if (!result.success || !result.contextJson) {
        throw new Error(result.error || 'Remote scan failed');
      }

      // Parse context JSON and map to findings
      const contextData = JSON.parse(result.contextJson);
      const findings = (contextData.iac_context || []).map((ctx: any) => 
        Mappers.mapIacContextToFinding(ctx)
      );

      // Get rule codes for findings
      const findingsWithRuleCode = await Promise.all(
        findings.map((finding: Finding) =>
          this.iacScanner.getRuleCode(
            finding.getId(),
            finding,
            this.containerEnginePath,
            scanConfiguration.getContainerImageName(),
            this.toolVersion
          )
        )
      );

      const scannerRes = new ScannerRes(result.success, findingsWithRuleCode);
      return scannerRes;
    } finally {
      // Cleanup replaced files if necessary
      if (scanLocation !== folderToScan) {
        await this.cleanFolder(folderToScan);
      }
    }
  }

  private async executeScanViaLocal(
    folderToScan: string,
    outputChannel: OutputChannel,
    scanConfiguration: ScanConfiguration,
    scanLoader: any
  ): Promise<ScannerRes> {
    // Process variable replacement if needed
    const scanLocation = await this.prepareFilesForScan(folderToScan, outputChannel, scanConfiguration);

    const scannerRes: ScannerRes = await this.iacScanner.scan(
      scanLocation,
      outputChannel,
      scanConfiguration.getContainerImageName(),
      scanConfiguration.getIacTool(),
      this.toolVersion,
      this.containerEnginePath,
      scanLoader
    ).finally(() => {
      if (scanLocation !== folderToScan) {
        this.cleanFolder(folderToScan);
      }
    });

    const findingsWithRuleCode: Promise<Finding>[] = scannerRes.getFindings().map((finding: Finding) => {
      return this.iacScanner.getRuleCode(
        finding.getId(),
        finding,
        this.containerEnginePath,
        scanConfiguration.getContainerImageName(),
        this.toolVersion
      );
    });
    scannerRes.setFindings(await Promise.all(findingsWithRuleCode));
    return scannerRes;
  }

  private async prepareFilesForScan(
    folderToScan: string,
    outputChannel: OutputChannel,
    scanConfiguration: ScanConfiguration
  ): Promise<string> {
    let releaseIdData: IReleaseIdData;
    let variablesFromLibrary: { [key: string]: IVariableData } = {};
    let releaseEnvironments: number[] = [];
    let variableGroupsIds: number[] = [];
    let variableGroupsData: IVariableGroupData;
    let variableReplace: boolean = false;

    if (!scanConfiguration.isValidAdReplace()) {
      outputChannel.appendLine("Configuration values are missing≤ avoiding variable replace");
      return folderToScan;
    }

    variableReplace = true;
    releaseIdData = await this.fetchReleaseDefinitionData(scanConfiguration);
    variablesFromLibrary = releaseIdData.variables;
    releaseEnvironments = releaseIdData.environments
      .map((environment: { variableGroups: number[] }) => environment.variableGroups)
      .flat();
    const releaseVariableGroups = (releaseIdData as any).variableGroups || [];
    variableGroupsIds = [...new Set([...releaseEnvironments, ...releaseVariableGroups])];
    variableGroupsData = await this.fetchGroupIdData(scanConfiguration, this.variablesIdString(variableGroupsIds));
    variablesFromLibrary = this.combineVariables(variablesFromLibrary, variableGroupsData);

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

    return variableReplace ? path.join(folderToScan, 'replacedFiles') : folderToScan;
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
          replacedFile = replacedFile + "\n" + line;
        }
      } else {
        replacedFile = replacedFile + "\n" + line;
      }
    });

    return replacedFile;
  }

  private combineVariables(
    variablesFromLibrary: { [key: string]: IVariableData },
    variableGroupsData: IVariableGroupData
  ): { [key: string]: IVariableData } {
    const combinedVariables = { ...variablesFromLibrary };
    
    variableGroupsData.value.forEach(
      (variableGroup: { variables: { [x: string]: IVariableData } }) => {
        Object.keys(variableGroup.variables).forEach((variableName: string) => {
          combinedVariables[variableName] = variableGroup.variables[variableName];
        });
      }
    );
    
    return combinedVariables;
  }

  private variablesIdString(variableGroupsIds: number[]): string {
    let variableGroupsIdsString: string = "";
    variableGroupsIds.forEach((id: number) => {
      variableGroupsIdsString =
        variableGroupsIdsString === "" ? id.toString() : variableGroupsIdsString + "," + id.toString();
    });
    return variableGroupsIdsString;
  }

  private async fetchReleaseDefinitionData(scanConfiguration: ScanConfiguration): Promise<IReleaseIdData> {
    return (await this.restClient.get(
      VARIABLE_GROUPS_AD_BY_RELEASE_DEFINITION_ID
        .replace("{organization}", scanConfiguration.getOrganizationName())
        .replace("{project}", scanConfiguration.getProjectName())
        .replace("{definitionId}", scanConfiguration.getDefinitionId()),
      AuthEncoder.encode(
        scanConfiguration.getAdUserName(),
        scanConfiguration.getAdPersonalAccessToken()
      )
    )) as IReleaseIdData;
  }

  private async fetchGroupIdData(scanConfiguration: ScanConfiguration, groupIds: string): Promise<IVariableGroupData> {
    return (await this.restClient.get(
      VARIABLE_GROUPS_AD_BY_ID
        .replace("{organization}", scanConfiguration.getOrganizationName())
        .replace("{project}", scanConfiguration.getProjectName())
        .replace("{groupIds}", groupIds),
      AuthEncoder.encode(
        scanConfiguration.getAdUserName(),
        scanConfiguration.getAdPersonalAccessToken()
      )
    )) as IVariableGroupData;
  }

}
