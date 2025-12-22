class ThresholdRisk:
    """
    Model for threshold configuration in engine_risk.
    Supports both static configuration and dynamic QUALITY_VULNERABILITY_MANAGEMENT.
    """

    def __init__(self, data):
        self.quality_vulnerability_management = data.get(
            "QUALITY_VULNERABILITY_MANAGEMENT"
        )
