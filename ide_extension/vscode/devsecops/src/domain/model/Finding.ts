export class Finding {

    private id: string;
    private severity: string;
    private where: string;
    private description: string;
    private module: string;
    private tool: string;
    private references: string[];
    private additionalFields: { [key: string]: string | undefined } = {};
    
    constructor(
        id: string,
        severity: string,
        where: string,
        description: string,
        module: string,
        tool: string,
        references: string[] = [],
        additionalFields: { [key: string]: string | undefined } = {}
    ) {
        this.id = id;
        this.severity = severity;
        this.where = where;
        this.description = description;
        this.module = module;
        this.tool = tool;
        this.references = references;
        this.additionalFields = additionalFields;
    }

    public getId(): string {
        return this.id;
    }

    public getSeverity(): string {
        return this.severity;
    }

    public getWhere(): string {
        return this.where;
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

    public getAdditionalField(key: string): string | undefined {
        return this.additionalFields[key];
    }

    public getAllAdditionalFields(): { [key: string]: string | undefined } {
        return this.additionalFields;
    }
}