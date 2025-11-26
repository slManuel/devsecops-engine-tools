from abc import ABCMeta, abstractmethod


class RiskScoreGateway(metaclass=ABCMeta):
    @abstractmethod
    def get_risk_score(self, finding_list, config_tool):
        "get_risk_score"