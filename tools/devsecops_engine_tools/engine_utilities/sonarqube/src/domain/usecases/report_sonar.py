from devsecops_engine_tools.engine_utilities.sonarqube.src.infrastructure.helpers.utils import (
    set_repository
)
from devsecops_engine_tools.engine_core.src.infrastructure.helpers.util import (
    define_env
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.vulnerability_management_gateway import (
    VulnerabilityManagementGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.vulnerability_management import (
    VulnerabilityManagement
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.secrets_manager_gateway import (
    SecretsManagerGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway import (
    DevopsPlatformGateway
)
from devsecops_engine_tools.engine_utilities.sonarqube.src.domain.model.gateways.sonar_gateway import (
    SonarGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.input_core import (
    InputCore
)
from typing import Optional
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

class ReportSonar:
    def __init__(
        self,
        vulnerability_management_gateway: VulnerabilityManagementGateway,
        secrets_manager_gateway: SecretsManagerGateway,
        devops_platform_gateway: DevopsPlatformGateway,
        remote_config_source_gateway: DevopsPlatformGateway,
        sonar_gateway: SonarGateway
    ):
        self.vulnerability_management_gateway = vulnerability_management_gateway
        self.secrets_manager_gateway = secrets_manager_gateway
        self.devops_platform_gateway = devops_platform_gateway
        self.remote_config_source_gateway = remote_config_source_gateway
        self.sonar_gateway = sonar_gateway

    def process(self, args):
        pipeline_name = self.devops_platform_gateway.get_variable("pipeline_name")
        branch = self.devops_platform_gateway.get_variable("branch_tag").replace("refs/heads/", "")
        input_core = self._build_input_core()

        source_code_management_uri = set_repository(
            pipeline_name,
            self.devops_platform_gateway.get_source_code_management_uri()
        )
        config_tool = self.remote_config_source_gateway.get_remote_config(
            args["remote_config_repo"],
            "/engine_core/ConfigTool.json",
            args["remote_config_branch"]
        )
        environment = define_env(None, branch)
        secret, secret_tool = self._resolve_secret(args, config_tool)

        report_config_tool = self.remote_config_source_gateway.get_remote_config(
            args["remote_config_repo"],
            "/engine_integrations/report_sonar/ConfigTool.json",
            args["remote_config_branch"]
        )

        project_keys = self._resolve_project_keys(report_config_tool, pipeline_name)

        args["module"] = "sonarqube"
        vulnerability_manager = self._build_vulnerability_manager(
            args,
            input_core,
            secret_tool,
            config_tool,
            source_code_management_uri,
            branch,
            environment,
        )

        for project_key in project_keys:
            self._process_project(
                project_key,
                args,
                secret,
                secret_tool,
                config_tool,
                report_config_tool,
                pipeline_name,
                branch,
            )

            input_core.scope_pipeline = project_key
            input_core.scope_service = project_key

            self.vulnerability_management_gateway.send_vulnerability_management(
                vulnerability_management=vulnerability_manager
            )

        input_core.scope_pipeline = pipeline_name
        input_core.scope_service = pipeline_name
        return input_core

    def _build_input_core(self):
        return InputCore(
            [],
            {},
            "",
            "",
            "",
            "",
            self.devops_platform_gateway.get_variable("stage").capitalize(),
        )

    def _resolve_secret(self, args, config_tool):
        if args["use_secrets_manager"] != "true":
            return args, None

        secret = self.secrets_manager_gateway.get_secret(config_tool)
        secret_tool = secret.copy()
        sonar_instance = args.get("sonar_instance")
        if sonar_instance:
            instance_key = f"token_{sonar_instance.lower()}"
            secret["token_sonar"] = secret.get(instance_key, secret["token_sonar"])
        return secret, secret_tool

    def _resolve_project_keys(self, report_config_tool, pipeline_name):
        components = report_config_tool["PIPELINE_COMPONENTS"].get(pipeline_name)
        if not components:
            return self.sonar_gateway.get_project_keys(pipeline_name)

        project_keys = [f"{pipeline_name}_{component}" for component in components]
        print(f"Multiple project keys detected: {project_keys}")
        return project_keys

    def _build_vulnerability_manager(
        self,
        args,
        input_core,
        secret_tool,
        config_tool,
        source_code_management_uri,
        branch,
        environment,
    ):
        return VulnerabilityManagement(
            scan_type="SONARQUBE",
            input_core=input_core,
            dict_args=args,
            secret_tool=secret_tool,
            config_tool=config_tool,
            source_code_management_uri=source_code_management_uri,
            sonar_instance=args["sonar_instance"],
            repository_provider=self.devops_platform_gateway.get_variable("repository_provider"),
            access_token=self.devops_platform_gateway.get_variable("access_token"),
            version=self.devops_platform_gateway.get_variable("build_execution_id"),
            build_id=self.devops_platform_gateway.get_variable("build_id"),
            branch_tag=branch,
            commit_hash=self.devops_platform_gateway.get_variable("commit_hash"),
            environment=environment,
            vm_product_type_name=self.devops_platform_gateway.get_variable("vm_product_type_name"),
            vm_product_name=self.devops_platform_gateway.get_variable("vm_product_name"),
            vm_product_description=self.devops_platform_gateway.get_variable("vm_product_description"),
        )

    def _process_project(
        self,
        project_key,
        args,
        secret,
        secret_tool,
        config_tool,
        report_config_tool,
        pipeline_name,
        branch,
    ):
        try:
            filtered_findings = self._get_filtered_findings(project_key, args, secret_tool, config_tool)
            sonar_findings = self._get_sonar_findings(
                project_key,
                args,
                secret["token_sonar"],
                report_config_tool,
                pipeline_name,
                branch,
            )
            self._synchronize_findings(
                filtered_findings,
                sonar_findings,
                args,
                secret["token_sonar"],
                report_config_tool,
            )
        except Exception as error:
            logger.warning(f"It was not possible to synchronize Sonar and Vulnerability Manager: {error}")

    def _get_filtered_findings(self, project_key, args, secret_tool, config_tool):
        findings = self.vulnerability_management_gateway.get_all(
            service=project_key,
            dict_args=args,
            secret_tool=secret_tool,
            config_tool=config_tool,
        )[0]
        return self.sonar_gateway.filter_by_sonarqube_tag(findings)

    def _get_sonar_findings(
        self,
        project_key,
        args,
        sonar_token,
        report_config_tool,
        pipeline_name,
        branch,
    ):
        sonar_vulns_params, sonar_hotspots_params = self._build_query_params(
            project_key,
            report_config_tool,
            pipeline_name,
            branch,
        )
        sonar_vulnerabilities = self.sonar_gateway.get_findings(
            args["sonar_url"],
            sonar_token,
            "/api/issues/search",
            sonar_vulns_params,
            "issues",
            report_config_tool["MAX_RETRIES_QUERY_SONAR"],
        )
        sonar_hotspots = self.sonar_gateway.get_findings(
            args["sonar_url"],
            sonar_token,
            "/api/hotspots/search",
            sonar_hotspots_params,
            "hotspots",
            report_config_tool["MAX_RETRIES_QUERY_SONAR"],
        )
        return sonar_vulnerabilities + sonar_hotspots

    def _build_query_params(self, project_key, report_config_tool, pipeline_name, branch):
        sonar_vulns_params = {
            "componentKeys": project_key,
            "types": "VULNERABILITY",
            "ps": 500,
            "p": 1,
            "s": "CREATION_DATE",
            "asc": "false",
        }
        sonar_hotspots_params = {
            "projectKey": project_key,
            "ps": 100,
            "p": 1,
        }

        if report_config_tool["USE_BRANCH_PARAMETER"] and pipeline_name not in report_config_tool["USE_PULL_REQUEST_PARAMETER"]:
            sonar_vulns_params["branch"] = branch
            sonar_hotspots_params["branch"] = branch
            return sonar_vulns_params, sonar_hotspots_params

        pull_request_id = self._get_pull_request_id()
        if pull_request_id is not None:
            sonar_vulns_params["pullRequest"] = pull_request_id
            sonar_hotspots_params["pullRequest"] = pull_request_id
        return sonar_vulns_params, sonar_hotspots_params

    def _get_pull_request_id(self) -> Optional[int]:
        try:
            return int(self.devops_platform_gateway.get_variable("pull_request_id"))
        except (TypeError, ValueError):
            return None

    def _synchronize_findings(self, filtered_findings, sonar_findings, args, sonar_token, report_config_tool):
        for finding in filtered_findings:
            related_sonar_finding = self.sonar_gateway.search_finding_by_id(
                sonar_findings,
                finding.unique_id_from_tool,
            )
            if not related_sonar_finding:
                continue

            if related_sonar_finding.get("type") == "VULNERABILITY":
                self._update_issue_status(
                    finding,
                    related_sonar_finding,
                    args,
                    sonar_token,
                    report_config_tool,
                )
                continue

            self._update_hotspot_status(
                finding,
                related_sonar_finding,
                args,
                sonar_token,
                report_config_tool,
            )

    def _update_issue_status(self, finding, related_sonar_finding, args, sonar_token, report_config_tool):
        transition = self._resolve_issue_transition(finding, related_sonar_finding)
        if not transition:
            return

        self.sonar_gateway.change_finding_status(
            args["sonar_url"],
            sonar_token,
            "/api/issues/do_transition",
            {
                "issue": related_sonar_finding["key"],
                "transition": transition,
            },
            "issue",
            report_config_tool["MAX_RETRIES_QUERY_SONAR"],
        )

    def _resolve_issue_transition(self, finding, related_sonar_finding):
        if finding.active and related_sonar_finding["status"] == "RESOLVED":
            return "reopen"
        if related_sonar_finding["status"] == "RESOLVED":
            return None
        if finding.false_p:
            return "falsepositive"
        if finding.risk_accepted or finding.out_of_scope:
            return "wontfix"
        return None

    def _update_hotspot_status(self, finding, related_sonar_finding, args, sonar_token, report_config_tool):
        hotspot_payload = self._build_hotspot_payload(finding, related_sonar_finding)
        if not hotspot_payload:
            return

        self.sonar_gateway.change_finding_status(
            args["sonar_url"],
            sonar_token,
            "/api/hotspots/change_status",
            hotspot_payload,
            "hotspot",
            report_config_tool["MAX_RETRIES_QUERY_SONAR"],
        )

    def _build_hotspot_payload(self, finding, related_sonar_finding):
        status = None
        resolution = None
        current_status = related_sonar_finding["status"]

        if finding.active and current_status == "REVIEWED":
            status = "TO_REVIEW"
        elif current_status == "TO_REVIEW":
            if finding.false_p:
                resolution = "SAFE"
            elif finding.risk_accepted or finding.out_of_scope:
                resolution = "ACKNOWLEDGED"
            if resolution:
                status = "REVIEWED"

        if not status:
            return None

        payload = {
            "hotspot": related_sonar_finding["key"],
            "status": status,
        }
        if resolution:
            payload["resolution"] = resolution
        return payload