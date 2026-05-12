import { OutputChannel } from "vscode";
import { IIacScanUseCase } from "./interfaces/IIacScanUseCase";
import { IacScanner } from "../../infrastructure/scanners/IacScanner";
import { IRestClientGateway } from "../model/gateways/IRestClientGateway";
import {
  VARIABLE_GROUPS_AD_BY_RELEASE_DEFINITION_ID,
  VARIABLE_GROUPS_AD_BY_ID,
  VARIABLE_GROUPS_AD_BY_NAME,
} from "../../application/appService/Constants";
import { StringUtils } from "../../infrastructure/helper/StringUtils";
import { promises as fs } from "fs";
import * as path from "path";
import { ScannerRes } from "../model/ScannerRes";
import { ScanConfiguration } from "../model/ScanConfiguration";
import { Finding } from "../model/Finding";
import { ScanExecutionOrchestrator } from "../../infrastructure/executors/ScanExecutionOrchestrator";
import { IScanExecutionConfig } from "../../infrastructure/executors/IScanExecutor";
import { ScanContextMapper } from "../../infrastructure/mappers/ScanContextMapper";
import { MetricsService } from "../../infrastructure/services/MetricsService";
import { ScanConfigurationService } from "../../infrastructure/config/ScanConfigurationService";

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
    
    // Create MetricsService instance to capture logs during remote execution
    const metricsService = new MetricsService();
    metricsService.clearLogs();
    const startTime = Date.now();
    
    // Process variable replacement if needed (same as local)
    const scanLocation = await this.prepareFilesForScan(folderToScan, outputChannel, scanConfiguration);

    try {
      try {
        // Build config for remote execution
        const scanConfig: IScanExecutionConfig = {
          scanType: 'iac',
          target: scanLocation,
          containerImageName: scanConfiguration.getContainerImageName(),
          engineToolsVersion: this.toolVersion,
          iacTool: scanConfiguration.getIacTool()
        };

        // Execute via remote microservice with log capture
        const logCapture = (message: string) => metricsService.captureOnly(message);
        const result = await executor.execute(scanConfig, outputChannel, logCapture);

        if (!result.success || !result.contextJson) {
          throw new Error(result.error || 'Remote scan failed');
        }

        // Parse context JSON and map to findings using centralized mapper
        const mappedResult = ScanContextMapper.parseAndMapContext(result.contextJson, 'iac');
        
        if (!mappedResult.success) {
          throw new Error(mappedResult.errorMessage || 'Failed to parse scan results');
        }
        
        const findings = mappedResult.findings;

        // Get rule codes for findings
        const customRulesUrl = ScanConfigurationService.getCustomRulesUrl();
        const findingsWithRuleCode = customRulesUrl
          ? await Promise.all(findings.map((finding: Finding) =>
              this.iacScanner.getRuleCode(finding.getId(), finding)
            ))
          : findings;

        // Send metrics for remote execution (non-blocking)
        try {
          await metricsService.collectAndstoreMetricsData(
            folderToScan,
            findingsWithRuleCode,
            mappedResult.severityCounts,
            mappedResult.success,
            'engine_iac',
            'remote-microservice',
            result.executionTime ?? 0
          );
        } catch (metricsError) {
          // Log but don't fail the scan if metrics upload fails
          console.error('Failed to send metrics:', metricsError);
        }

        const scannerRes = new ScannerRes(mappedResult.success, findingsWithRuleCode, mappedResult.severityCounts);
        return scannerRes;
      } catch (error) {
        // Send metrics for failed scan before throwing error
        metricsService.captureError(outputChannel, error, 'remote scan execution');
        await metricsService.collectFailedScanMetrics(folderToScan, 'engine_iac', 'remote-microservice', Date.now() - startTime);
        throw error;
      }
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

    const customRulesUrl = ScanConfigurationService.getCustomRulesUrl();
    if (customRulesUrl) {
      const findingsWithRuleCode = await Promise.all(
        scannerRes.getFindings().map((finding: Finding) =>
          this.iacScanner.getRuleCode(finding.getId(), finding)
        )
      );
      scannerRes.setFindings(findingsWithRuleCode);
    }
    return scannerRes;
  }

  private async prepareFilesForScan(
    folderToScan: string,
    outputChannel: OutputChannel,
    scanConfiguration: ScanConfiguration
  ): Promise<string> {
    let variablesFromLibrary: { [key: string]: IVariableData } = {};
    let variableReplace: boolean = false;

    if (scanConfiguration.isValidReleasePipelineReplace()) {
      // Case 1: Release pipeline — fetch variables from release definition + all linked variable groups
      outputChannel.appendLine("🔗 Release pipeline mode: fetching variables from release definition");
      const releaseIdData = await this.fetchReleaseDefinitionData(scanConfiguration);
      variablesFromLibrary = releaseIdData.variables;
      const releaseEnvironments = releaseIdData.environments
        .map((environment: { variableGroups: number[] }) => environment.variableGroups)
        .flat();
      const releaseVariableGroups = (releaseIdData as any).variableGroups || [];
      const variableGroupsIds = [...new Set([...releaseEnvironments, ...releaseVariableGroups])];
      const variableGroupsData = await this.fetchGroupIdData(scanConfiguration, this.variablesIdString(variableGroupsIds));
      variablesFromLibrary = this.combineVariables(variablesFromLibrary, variableGroupsData);
      variableReplace = true;

      // If groupName is also defined, fetch it on top and override with its values
      const groupName = scanConfiguration.getGroupName();
      if (groupName) {
        outputChannel.appendLine(`🏗️ groupName also defined: merging variables from group "${groupName}" (overrides release variables)`);
        try {
          const extraGroupData = await this.fetchGroupByNameData(scanConfiguration, groupName);
          variablesFromLibrary = this.combineVariables(variablesFromLibrary, extraGroupData);
        } catch (error) {
          outputChannel.appendLine(`⚠️ Could not fetch variable group "${groupName}": ${error}`);
        }
      }
    } else if (scanConfiguration.isValidBuildPipelineReplace()) {
      // Case 2: Build pipeline — fetch variables from the specific variable group by name
      const groupName = scanConfiguration.getGroupName();
      outputChannel.appendLine(`🏗️ Build pipeline mode: fetching variables from group "${groupName}"`);
      const groupData = await this.fetchGroupByNameData(scanConfiguration, groupName);
      variablesFromLibrary = this.combineVariables(variablesFromLibrary, groupData);
      variableReplace = true;
    } else {
      if (scanConfiguration.hasValidAzureDevOpsConfig()) {
        outputChannel.appendLine("⚠️ Variable replacement skipped: 'releaseId' or 'groupName' must be configured in Azure DevOps settings to enable variable replacement");
      } else {
        outputChannel.appendLine("⚠️ Azure DevOps configuration is missing or incomplete (organizationName, projectName, username and personalAccessToken are required) — skipping variable replacement");
      }
      return folderToScan;
    }

    this.files = await fs.readdir(folderToScan);
    const regex = /#{|}#/;
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
      const supportedExtensions = ['.yml', '.yaml', '.json', '.tf', '.bicep'];
      const fileName = file.toLowerCase();
      const isSupportedFile = fileName.includes('dockerfile') ||
        supportedExtensions.some(ext => fileName.endsWith(ext));
      if (!isSupportedFile) {
        outputChannel.append(`⏭️ Skipping unsupported file type: ${file}\n`);
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

    if (variableReplace) {
      await this.injectParamsAsDefaults(replacedFilesDir, outputChannel);
    }

    return variableReplace ? path.join(folderToScan, 'replacedFiles') : folderToScan;
  }

  /**
   * CloudFormation support: discovers all params*.json files and injects each ParameterValue
   * as the Default of the matching parameter in the corresponding template*.yaml/yml.
   * Pairing convention: params{suffix}.json → template{suffix}.yaml/yml
   * Examples: params.json→template.yaml, params-s3.json→template-s3.yaml
   * This allows Checkov to resolve !Ref with real values instead of leaving them undefined.
   */
  private async injectParamsAsDefaults(
    dir: string,
    outputChannel: OutputChannel
  ): Promise<void> {
    const allFiles = await fs.readdir(dir);

    // Find all params*.json files and resolve their matching template
    const paramsFiles = allFiles.filter(f => /^params.*\.json$/i.test(f));
    if (paramsFiles.length === 0) {
      return;
    }

    for (const paramsFile of paramsFiles) {
      // Extract suffix: "params.json" → "", "params-s3.json" → "-s3"
      const suffix = paramsFile.replace(/^params/i, '').replace(/\.json$/i, '');

      const templateFile = allFiles.find(f =>
        f.toLowerCase() === `template${suffix.toLowerCase()}.yaml` ||
        f.toLowerCase() === `template${suffix.toLowerCase()}.yml`
      );

      if (!templateFile) {
        outputChannel.appendLine(`⚠️ ${paramsFile} found but no matching template${suffix}.yaml/yml — skipping`);
        continue;
      }

      // Parse params file — supports [{ParameterKey, ParameterValue}] or {Key: Value}
      let params: Record<string, string> = {};
      try {
        const raw = JSON.parse(await fs.readFile(path.join(dir, paramsFile), 'utf-8'));
        if (Array.isArray(raw)) {
          raw.forEach((entry: { ParameterKey: string; ParameterValue: string }) => {
            if (entry.ParameterKey !== undefined && entry.ParameterValue !== undefined) {
              params[entry.ParameterKey] = String(entry.ParameterValue);
            }
          });
        } else if (typeof raw === 'object' && raw !== null) {
          Object.entries(raw).forEach(([k, v]) => { params[k] = String(v); });
        }
      } catch (e) {
        outputChannel.appendLine(`⚠️ Could not parse ${paramsFile}: ${e}`);
        continue;
      }

      if (Object.keys(params).length === 0) {
        continue;
      }

      outputChannel.appendLine(`📥 Injecting ${Object.keys(params).length} param(s) from ${paramsFile} into ${templateFile}`);
      await this.injectDefaultsIntoTemplate(path.join(dir, templateFile), params);
    }
  }

  private async injectDefaultsIntoTemplate(
    templatePath: string,
    params: Record<string, string>
  ): Promise<void> {
    const unresolvedPattern = /#{[^}]+}#/;

    // Pre-filter params: skip any whose value still contains an unreplaced placeholder
    const resolvedParams: Record<string, string> = {};
    for (const [key, value] of Object.entries(params)) {
      if (unresolvedPattern.test(value)) {
        // skip unresolved placeholders silently
      } else {
        resolvedParams[key] = value;
      }
    }

    const lines = (await fs.readFile(templatePath, 'utf-8')).split('\n');
    const result: string[] = [];
    let inParameters = false;
    let currentParam: string | null = null;
    let defaultInjected = false;

    for (const line of lines) {
      const trimmed = line.trimEnd();

      // Detect top-level Parameters: section
      if (/^Parameters\s*:/.test(trimmed)) {
        inParameters = true;
        result.push(trimmed);
        continue;
      }

      // Leaving Parameters section when a new top-level key appears
      if (inParameters && /^[A-Za-z]/.test(trimmed) && !/^\s/.test(trimmed)) {
        if (currentParam && !defaultInjected && resolvedParams[currentParam] !== undefined) {
          this.injectBeforeTrailingBlanks(result, `    Default: ${resolvedParams[currentParam]}`);
        }
        inParameters = false;
        currentParam = null;
      }

      if (inParameters) {
        // Detect a parameter name (2-space indented key)
        const paramMatch = trimmed.match(/^  ([A-Za-z0-9_]+)\s*:/);
        if (paramMatch) {
          if (currentParam && !defaultInjected && resolvedParams[currentParam] !== undefined) {
            this.injectBeforeTrailingBlanks(result, `    Default: ${resolvedParams[currentParam]}`);
          }
          currentParam = paramMatch[1];
          defaultInjected = false;
          result.push(trimmed);
          continue;
        }

        // Detect existing Default: line
        const defaultMatch = trimmed.match(/^    Default\s*:/);
        if (defaultMatch) {
          if (currentParam && resolvedParams[currentParam] !== undefined) {
            // Override existing default with resolved param value
            result.push(`    Default: ${resolvedParams[currentParam]}`);
          } else if (currentParam && params[currentParam] !== undefined) {
            // Param exists but was unresolved — keep original default
            result.push(trimmed);
          } else {
            // No param for this key — keep original default untouched
            result.push(trimmed);
          }
          defaultInjected = true;
          continue;
        }
      }

      result.push(trimmed);
    }

    // Handle last parameter in file
    if (currentParam && !defaultInjected && resolvedParams[currentParam] !== undefined) {
      this.injectBeforeTrailingBlanks(result, `    Default: ${resolvedParams[currentParam]}`);
    }

    await fs.writeFile(templatePath, result.join('\n'), 'utf-8');
  }

  /** Inserts a line before any trailing blank lines or comment lines at the end of the result array. */
  private injectBeforeTrailingBlanks(result: string[], line: string): void {
    let trailingCount = 0;
    while (trailingCount < result.length) {
      const t = result[result.length - 1 - trailingCount].trim();
      if (t === '' || t.startsWith('#')) {
        trailingCount++;
      } else {
        break;
      }
    }
    result.splice(result.length - trailingCount, 0, line);
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
      try {
        const varPattern = /#{([^}]+)}#/g;
        const replacedLine = line.replace(varPattern, (match, variableName) => {
          if (variablesFromLibrary[variableName] && variableReplace) {
            outputChannel.append(`✅ Variable ${variableName} replaced in file ${file}\n`);
            return variablesFromLibrary[variableName].value;
          } else {
            outputChannel.append(`⚠️ Variable ${variableName} not found in library for file ${file}\n`);
            return match;
          }
        });
        replacedFile = replacedFile + "\n" + replacedLine;
      } catch (lineError) {
        outputChannel.append(`⚠️ Skipping unprocessable line in file ${file}: ${lineError}\n`);
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
      StringUtils.encodeBasicAuth(
        scanConfiguration.getAdUserName(),
        scanConfiguration.getAdPersonalAccessToken()
      )
    )) as IReleaseIdData;
  }

  private async fetchGroupByNameData(scanConfiguration: ScanConfiguration, groupName: string): Promise<IVariableGroupData> {
    return (await this.restClient.get(
      VARIABLE_GROUPS_AD_BY_NAME
        .replace("{organization}", scanConfiguration.getOrganizationName())
        .replace("{project}", scanConfiguration.getProjectName())
        .replace("{groupName}", encodeURIComponent(groupName)),
      StringUtils.encodeBasicAuth(
        scanConfiguration.getAdUserName(),
        scanConfiguration.getAdPersonalAccessToken()
      )
    )) as IVariableGroupData;
  }

  private async fetchGroupIdData(scanConfiguration: ScanConfiguration, groupIds: string): Promise<IVariableGroupData> {
    return (await this.restClient.get(
      VARIABLE_GROUPS_AD_BY_ID
        .replace("{organization}", scanConfiguration.getOrganizationName())
        .replace("{project}", scanConfiguration.getProjectName())
        .replace("{groupIds}", groupIds),
      StringUtils.encodeBasicAuth(
        scanConfiguration.getAdUserName(),
        scanConfiguration.getAdPersonalAccessToken()
      )
    )) as IVariableGroupData;
  }

}
