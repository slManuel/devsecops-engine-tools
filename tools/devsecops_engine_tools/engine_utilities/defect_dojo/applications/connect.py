from devsecops_engine_tools.engine_utilities.utils.api_error import ApiError
from devsecops_engine_tools.engine_utilities.defect_dojo.domain.request_objects.import_scan import ImportScanRequest
from devsecops_engine_tools.engine_utilities.defect_dojo.domain.serializers.import_scan import ImportScanSerializer
from devsecops_engine_tools.engine_utilities.defect_dojo.domain.user_case.cmdb import CmdbUserCase
from devsecops_engine_tools.engine_utilities.defect_dojo.infraestructure.driver_adapters.cmdb import CmdbRestConsumer
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.azure.azure_devops import AzureDevops
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions import GithubActions
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.runtime_local.runtime_local import RuntimeLocal
from devsecops_engine_tools.engine_utilities.utils.session_manager import SessionManager


class Connect:
    @staticmethod
    # Configuration Management Database aws
    def cmdb(**kwargs) -> ImportScanRequest:
        try:
            request: ImportScanRequest = ImportScanSerializer().load(kwargs)
            rc = CmdbRestConsumer(
                token=request.token_cmdb,
                host=request.host_cmdb,
                mapping_cmdb=request.cmdb_mapping,
                session=SessionManager(),
            )

            remote_config_source_gateway = {
                "azure": AzureDevops(),
                "github": GithubActions(),
                "local": RuntimeLocal()
            }.get(request.remote_config_source.lower())

            uc = CmdbUserCase(rest_consumer_cmdb=rc, remote_config_source_gateway=remote_config_source_gateway, expression=request.expression)
            response = uc.execute(request)
        except Exception as e:
            return e

        return response
    
    def get_code_app(engagement_name, expression):
        uc = CmdbUserCase(rest_consumer_cmdb=None, remote_config_source_gateway=None, expression=expression)
        return uc.get_code_app(engagement_name)
