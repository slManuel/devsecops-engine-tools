from typing import List
from devsecops_engine_tools.engine_dast.src.domain.model.api_operation import ApiOperation


class ApiConfig():
    def __init__(self, api_data: dict):
        try:
            self.target_type: str = "API"
            self.endpoint: str = api_data["endpoint"]
            self.operations: "List[ApiOperation]" = api_data["operations"]
            self.concurrency: int = None
            self.rate_limit: int = None
            self.response_size: int = None
            self.bulk_size: int = None
            self.timeout: int = None

        except KeyError:
            raise KeyError("Missing configuration, validate the endpoint and every single operation")