import * as vscode from "vscode";

export class ScanConfiguration {
  private containerImageName: string;
  private containerImageVersion: string;
  private organizationName: string;
  private projectName: string;
  private definitionId: string;
  private environment: string;
  private adUserName: string;
  private adPersonalAccessToken: string;
  private dependenciesToken: string;
  private xrayMode: string;
  private dependenciesTool: string;
  private dependencyCheckDatabase: string;

  constructor() {
    this.containerImageName = "";
    this.containerImageVersion = "";
    this.organizationName = "";
    this.projectName = "";
    this.definitionId = "";
    this.environment = "dev";
    this.adUserName = "";
    this.adPersonalAccessToken = "";
    this.dependenciesToken = "";
    this.xrayMode = "";
    this.dependenciesTool = "";
    this.dependencyCheckDatabase = "";

    this.loadFromVSCodeConfig();
  }

  private loadFromVSCodeConfig(): void {
    const generalConfig = vscode.workspace.getConfiguration("devsecops.general");
    const azureDevopsConfig = vscode.workspace.getConfiguration("devsecops.azuredevops");
    const dependenciesConfig = vscode.workspace.getConfiguration("devsecops.dependencies");
    
    this.containerImageName = generalConfig.get("imageToUse") || "bancolombia/devsecops-engine-tools";
    this.containerImageVersion = generalConfig.get("imageVersion") || "";
    this.organizationName = azureDevopsConfig.get("organizationName") || "";
    this.projectName = azureDevopsConfig.get("projectName") || "";
    this.definitionId = azureDevopsConfig.get("releaseId") || "";
    this.environment = azureDevopsConfig.get("environment") || "dev";
    this.adUserName = azureDevopsConfig.get("username") || "";
    this.adPersonalAccessToken = azureDevopsConfig.get("personalAccessToken") || "";
    this.dependenciesToken = dependenciesConfig.get("dependenciesToken") || "";
    this.xrayMode = dependenciesConfig.get("xrayMode") || "audit";
    this.dependenciesTool = dependenciesConfig.get("dependenciesTool") || "xray";
    this.dependencyCheckDatabase = dependenciesConfig.get("dependencyCheckDatabase") || "";
  }

  public refresh(): void {
    this.loadFromVSCodeConfig();
  }

  public isValidAdReplace(): boolean {
    return (
      this.organizationName !== "" &&
      this.projectName !== "" &&
      this.definitionId !== "" &&
      this.adUserName !== "" &&
      this.adPersonalAccessToken !== ""
    );
  }

  public hasValidAdAuthentication(): boolean {
    return this.adUserName !== "" && this.adPersonalAccessToken !== "";
  }

  public getContainerImageName(): string {
    return this.containerImageName;
  }

  public getContainerImageVersion(): string {
    return this.containerImageVersion;
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

  public getEnvironment(): string {
    return this.environment;
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

  public async setContainerImageVersion(version: string): Promise<void> {
    const config = vscode.workspace.getConfiguration('devsecops.general');

    const targetScope = vscode.workspace.workspaceFolders 
      ? vscode.ConfigurationTarget.Workspace 
      : vscode.ConfigurationTarget.Global;
    
    await config.update('imageVersion', version, targetScope);
    this.containerImageVersion = version;
    
    console.log(`Saved container image version "${version}" to ${targetScope === vscode.ConfigurationTarget.Workspace ? 'Workspace' : 'Global'} settings`);
  }
}