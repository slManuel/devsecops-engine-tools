import * as vscode from "vscode";

export class ScanConfiguration {
  private dockerImageName: string;
  private dockerImageVersion: string;
  private organizationName: string;
  private projectName: string;
  private definitionId: string;
  private environment: string;
  private adUserName: string;
  private adPersonalAccessToken: string;
  private dependenciesToken: string;
  private xrayMode: string;
  private dependenciesTool: string;

  constructor() {
    this.dockerImageName = "";
    this.dockerImageVersion = "";
    this.organizationName = "";
    this.projectName = "";
    this.definitionId = "";
    this.environment = "dev";
    this.adUserName = "";
    this.adPersonalAccessToken = "";
    this.dependenciesToken = "";
    this.xrayMode = "";
    this.dependenciesTool = "";

    this.loadFromVSCodeConfig();
  }

  private loadFromVSCodeConfig(): void {
    const generalConfig = vscode.workspace.getConfiguration("devsecops.general");
    const azureDevopsConfig = vscode.workspace.getConfiguration("devsecops.azuredevops");
    const dependenciesConfig = vscode.workspace.getConfiguration("devsecops.dependencies");
    
    this.dockerImageName = generalConfig.get("imageToUse") || "bancolombia/devsecops-engine-tools";
    this.dockerImageVersion = generalConfig.get("imageVersion") || "1.72.0";
    this.organizationName = azureDevopsConfig.get("organizationName") || "";
    this.projectName = azureDevopsConfig.get("projectName") || "";
    this.definitionId = azureDevopsConfig.get("releaseId") || "";
    this.environment = azureDevopsConfig.get("environment") || "dev";
    this.adUserName = azureDevopsConfig.get("username") || "";
    this.adPersonalAccessToken = azureDevopsConfig.get("personalAccessToken") || "";
    this.dependenciesToken = dependenciesConfig.get("dependenciesToken") || "";
    this.xrayMode = dependenciesConfig.get("xrayMode") || "audit";
    this.dependenciesTool = dependenciesConfig.get("dependenciesTool") || "xray";
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

  public getDockerImageName(): string {
    return this.dockerImageName;
  }

  public getDockerImageVersion(): string {
    return this.dockerImageVersion;
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

}