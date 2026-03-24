import { getEffectiveSeverity as getEffectiveSeverityHelper } from "./ClassificationModel";

export class Finding {

    private id: string;
    private severity: string;
    private where: string;
    private description: string;
    private module: string;
    private tool: string;
    private references: string[];
    private additionalFields: { [key: string]: string | undefined } = {};
    private validationRuleCode?: string;
    private priority: string;
    
    constructor(
        id: string,
        severity: string,
        priority: string = "",
        where: string,
        description: string,
        module: string,
        tool: string,
        references: string[] = [],
        additionalFields: { [key: string]: string | undefined } = {},
        validationRuleCode?: string
    ) {
        this.id = id;
        this.severity = severity;
        this.where = where;
        this.description = description;
        this.module = module;
        this.tool = tool;
        this.references = references;
        this.additionalFields = additionalFields;
        this.validationRuleCode = validationRuleCode;
        this.priority = priority;
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

    public getValidationRuleCode(): string | undefined {
        return this.validationRuleCode;
    }

    public setValidationRuleCode(validationRuleCode: string): void {
        this.validationRuleCode = validationRuleCode;
    }

    public getPriority(): string {
        return this.priority;
    }

    public setPriority(priority: string): void {
        this.priority = priority;
    }

    /**
     * Gets the effective severity based on the current classification model configuration
     * If the model is "priority", returns the mapped priority value
     * Otherwise, returns the standard severity
     */
    public getEffectiveSeverity(): string {
        return getEffectiveSeverityHelper(this.severity, this.priority);
    }

}