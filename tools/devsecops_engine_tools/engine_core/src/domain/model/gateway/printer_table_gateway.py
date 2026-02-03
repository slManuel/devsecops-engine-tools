from abc import ABCMeta, abstractmethod
from devsecops_engine_tools.engine_core.src.domain.model.finding import (
    Finding,
)
from devsecops_engine_tools.engine_core.src.domain.model.report import (
    Report,
)

class PrinterTableGateway(metaclass=ABCMeta):
    @abstractmethod
    def print_table_findings(self, finding_list: "list[Finding]", break_build_manager):
        "print_table_findings"

    @abstractmethod
    def print_table_report(self, report_list: "list[Report]", finding_score_model):
        "print_table_report"

    @abstractmethod
    def print_table_exclusions(self, exclusions_list, break_build_manager):
        "print_table_exclusions"