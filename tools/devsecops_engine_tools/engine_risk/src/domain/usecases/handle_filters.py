import copy


class HandleFilters:
    def filter(self, findings):
        active_findings = self._get_active_findings(findings)
        self._get_priority_vulnerability(active_findings)
        return active_findings

    def filter_tags_days(self, devops_platform_gateway, remote_config, findings):
        tag_exclusion_days = remote_config["TAG_EXCLUSION_DAYS"]
        filtered_findings = []
        filtered = 0

        for finding in findings:
            exclude = False
            for tag in finding.tags:
                if tag in tag_exclusion_days and finding.age < tag_exclusion_days[tag]:
                    filtered += 1
                    exclude = True
                    print(
                        devops_platform_gateway.message(
                            "warning",
                            f"Report {finding.vm_id} with tag '{tag}' and age {finding.age} days is being excluded. It will be considered in {tag_exclusion_days[tag] - finding.age} days.",
                        )
                    )
                    break
            if not exclude:
                filtered_findings.append(finding)

        return filtered_findings, filtered

    def _get_active_findings(self, findings):
        return list(
            filter(
                lambda finding: finding.active,
                findings,
            )
        )

    def _get_priority_vulnerability(self, findings):
        for finding in findings:
            found_cve = False
            for vul in finding.id:
                if vul["vulnerability_id"].startswith("CVE"):
                    finding.id = vul["vulnerability_id"]
                    found_cve = True
                    break
            if not found_cve and finding.id:
                finding.id = finding.id[0]["vulnerability_id"]
