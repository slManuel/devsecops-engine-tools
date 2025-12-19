class ThresholdRisk:
    """
    Model for threshold configuration in engine_risk.
    Supports both static configuration and dynamic QUALITY_VULNERABILITY_MANAGEMENT.
    """
    def __init__(self, data):
        self.remediation_rate = data.get("REMEDIATION_RATE", {})
        self.score = data.get("SCORE", 0)
        self.quality_vulnerability_management = data.get("QUALITY_VULNERABILITY_MANAGEMENT")

    def to_dict(self):
        """Convert threshold to dictionary format for engine_risk"""
        return {
            "REMEDIATION_RATE": self.remediation_rate,
            "SCORE": self.score
        }
