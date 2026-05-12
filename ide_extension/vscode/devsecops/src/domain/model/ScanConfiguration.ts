import * as vscode from "vscode";

export class ScanConfiguration {
  private containerImageName: string;
  private organizationName: string;
  private projectName: string;
  private definitionId: string;
  private adUserName: string;
  private adPersonalAccessToken: string;
  private dependenciesToken: string;
  private xrayMode: string;
  private dependenciesTool: string;
  private dependencyCheckDatabase: string;
  private iacTool: string;
  private engineToolsVersion: string;
  private groupName: string;

  constructor() {
    this.containerImageName = "";
    this.organizationName = "";
    this.projectName = "";
    this.definitionId = "";
    this.adUserName = "";
    this.adPersonalAccessToken = "";
    this.dependenciesToken = "";
    this.xrayMode = "";
    this.dependenciesTool = "";
    this.dependencyCheckDatabase = "";
    this.iacTool = "";
    this.engineToolsVersion = "";
    this.groupName = "";

    this.loadFromVSCodeConfig();
  }

  private loadFromVSCodeConfig(): void {
    const generalConfig = vscode.workspace.getConfiguration("devsecops.general");
    const azureDevopsConfig = vscode.workspace.getConfiguration("devsecops.azuredevops");
    const dependenciesConfig = vscode.workspace.getConfiguration("devsecops.dependencies");
    const iacConfig = vscode.workspace.getConfiguration("devsecops.iac");
    
    this.containerImageName = generalConfig.get("imageToUse") || "bancolombia/devsecops-engine-tools:ide-v1";
    this.organizationName = azureDevopsConfig.get("organizationName") || "";
    this.projectName = azureDevopsConfig.get("projectName") || "";
    this.definitionId = azureDevopsConfig.get("releaseId") || "";
    this.adUserName = azureDevopsConfig.get("username") || "";
    this.adPersonalAccessToken = azureDevopsConfig.get("personalAccessToken") || "";
    this.dependenciesToken = dependenciesConfig.get("dependenciesToken") || "";
    this.xrayMode = dependenciesConfig.get("xrayMode") || "audit";
    this.dependenciesTool = dependenciesConfig.get("dependenciesTool") || "xray";
    this.dependencyCheckDatabase = dependenciesConfig.get("dependencyCheckDatabase") || "";
    this.iacTool = iacConfig.get("iacTool") || "checkov";
    this.engineToolsVersion = generalConfig.get("engineToolsVersion") || "";
    this.groupName = azureDevopsConfig.get("groupName") || "";
  }

  public refresh(): void {
    this.loadFromVSCodeConfig();
  }

  // Base Azure DevOps connectivity (org + project + credentials)
  public hasValidAzureDevOpsConfig(): boolean {
    return (
      this.organizationName !== "" &&
      this.projectName !== "" &&
      this.adUserName !== "" &&
      this.adPersonalAccessToken !== ""
    );
  }

  // Release pipeline: base config + releaseId
  public isValidReleasePipelineReplace(): boolean {
    return this.hasValidAzureDevOpsConfig() && this.definitionId !== "";
  }

  // Build pipeline: base config + groupName
  public isValidBuildPipelineReplace(): boolean {
    return this.hasValidAzureDevOpsConfig() && this.groupName !== "";
  }

  public isValidAdReplace(): boolean {
    return this.isValidReleasePipelineReplace() || this.isValidBuildPipelineReplace();
  }

  public hasValidAdAuthentication(): boolean {
    return this.adUserName !== "" && this.adPersonalAccessToken !== "";
  }

  public getContainerImageName(): string {
    return this.containerImageName;
  }

  public getContainerImageVersion(): string {
    return this.engineToolsVersion;
  }

  public getEngineToolsVersion(): string {
    return this.engineToolsVersion;
  }

  public getOrganizationName(): string {
    return this.organizationName;
  }

  public getProjectName(): string {
    return this.projectName;
  }

  public getDefinitionId(): string {
    return this.definitionId;
  }

  public getAdUserName(): string {
    return this.adUserName;
  }

  public getAdPersonalAccessToken(): string {
    return this.adPersonalAccessToken;
  }

  public getDependenciesToken(): string {
    return this.dependenciesToken;
  }

  public getXrayMode(): string {
    return this.xrayMode;
  }

  public getDependenciesTool(): string {
    return this.dependenciesTool;
  }

  public getDependencyCheckDatabase(): string {
    return this.dependencyCheckDatabase;
  }

  public getIacTool(): string {
    return this.iacTool;
  }

  public getGroupName(): string {
    return this.groupName;
  }
}