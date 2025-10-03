import { Finding } from "./Finding";
import { ISeverityCounts } from "./mappers/Mappers";

export class ScannerRes {

    private status: boolean;
    private findings: Finding[];
    private severityCounts?: ISeverityCounts | null;

    constructor(status: boolean, findings: Finding[], severityCounts?: ISeverityCounts | null) {
        this.status = status;
        this.findings = findings;
        this.severityCounts = severityCounts;
    }

    public getStatus(): boolean {
        return this.status;
    }

    public getFindings(): Finding[] {
        return this.findings;
    }

    public setFindings(findings: Finding[]): void {
        this.findings = findings;
    }

    public getSeverityCounts(): ISeverityCounts | null | undefined {
        return this.severityCounts;
    }

    public setSeverityCounts(severityCounts: ISeverityCounts | null): void {
        this.severityCounts = severityCounts;
    }

}