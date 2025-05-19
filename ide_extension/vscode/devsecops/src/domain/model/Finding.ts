export class Finding {

    private id: string;
    private customVulnId: string;
    private checkName: string;
    private checkClass: string;
    private severity: string;
    private where: string;
    private resource: string;
    private description: string;
    private module: string;
    private tool: string;
    private vulnerability_status?: string;
    private target_image?: string;
    private installed_version?: string;
    private fixed_version?: string;
    private package_name?: string;
    private cvss_score?: string;
    private references: string[];

    constructor(
        id: string,
        customVulnId: string,
        checkName: string,
        checkClass: string,
        severity: string,
        where: string,
        resource: string,
        description: string,
        module: string,
        tool: string,
        vulnerability_status?: string,
        target_image?: string,
        installed_version?: string,
        fixed_version?: string,
        package_name?: string,
        cvss_score?: string,
        references: string[] = []
    ) {
        this.id = id;
        this.customVulnId = customVulnId;
        this.checkName = checkName;
        this.checkClass = checkClass;
        this.severity = severity;
        this.where = where;
        this.resource = resource;
        this.description = description;
        this.module = module;
        this.tool = tool;
        this.vulnerability_status = vulnerability_status;
        this.target_image = target_image;
        this.installed_version = installed_version;
        this.fixed_version = fixed_version;
        this.package_name = package_name;
        this.cvss_score = cvss_score;
        this.references = references;
    }

    public getId(): string {
        return this.id;
    }

    public getCustomVulnId(): string {
        return this.customVulnId;
    }

    public getCheckName(): string {
        return this.checkName;
    }

    public getCheckClass(): string {
        return this.checkClass;
    }

    public getSeverity(): string {
        return this.severity;
    }

    public getWhere(): string {
        return this.where;
    }

    public getResource(): string {
        return this.resource;
    }

    public getDescription(): string {
        return this.description;
    }

    public getModule(): string {
        return this.module;
    }

    public getTool(): string {
        return this.tool;
    }

    public getVulnerabilityStatus(): string | undefined {
        return this.vulnerability_status;
    }
    public getTargetImage(): string | undefined {
        return this.target_image;
    }

    public getInstalledVersion(): string | undefined {
        return this.installed_version;
    }

    public getFixedVersion(): string | undefined {
        return this.fixed_version;
    }

    public getPackageName(): string | undefined {
        return this.package_name;
    }

    public getCvssScore(): string | undefined {
        return this.cvss_score;
    }

    public getReferences(): string[] {
        return this.references;
    }

}