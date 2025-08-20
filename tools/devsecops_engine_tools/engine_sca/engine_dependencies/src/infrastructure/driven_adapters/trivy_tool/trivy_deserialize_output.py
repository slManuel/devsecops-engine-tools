from devsecops_engine_tools.engine_sca.engine_dependencies.src.domain.model.gateways.deserializator_gateway import (
    DeserializatorGateway,
)
from devsecops_engine_tools.engine_sca.engine_container.src.infrastructure.driven_adapters.trivy_tool.trivy_deserialize_output import (
    TrivyDeserializator,
)
from dataclasses import dataclass

@dataclass
class TrivyDeserializatorSBOM(DeserializatorGateway):
    def get_list_findings(self, results_scan_file, remote_config):
        return TrivyDeserializator().get_list_findings(results_scan_file)
