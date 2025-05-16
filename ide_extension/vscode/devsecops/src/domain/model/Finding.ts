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

    public getReferences(): string[] {
        return this.references;
    }

}