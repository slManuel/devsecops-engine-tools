import * as vscode from "vscode";

export class ScanConfiguration {
  private dockerImageName: string;
  private organizationName: string;
  private projectName: string;
  private definitionId: string;
  private environment: string;
  private adUserName: string;
  private adPersonalAccessToken: string;

  constructor() {
    this.dockerImageName = "";
    this.organizationName = "";
    this.projectName = "";
    this.definitionId = "";
    this.environment = "dev";
    this.adUserName = "";
    this.adPersonalAccessToken = "";
    
    this.loadFromVSCodeConfig();
  }

  private loadFromVSCodeConfig(): void {
    const generalConfig = vscode.workspace.getConfiguration("devsecops.general");
    const azureDevopsConfig = vscode.workspace.getConfiguration("devsecops.azuredevops");
    
    this.dockerImageName = generalConfig.get("imageToUse") || "bancolombia/devsecops-engine-tools";
    this.organizationName = azureDevopsConfig.get("organizationName") || "";
    this.projectName = azureDevopsConfig.get("projectName") || "";
    this.definitionId = azureDevopsConfig.get("releaseId") || "";
    this.environment = azureDevopsConfig.get("environment") || "dev";
    this.adUserName = azureDevopsConfig.get("username") || "";
    this.adPersonalAccessToken = azureDevopsConfig.get("personalAccessToken") || "";
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

}