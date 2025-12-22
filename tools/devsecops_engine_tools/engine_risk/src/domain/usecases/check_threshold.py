import re


class CheckThreshold:
    def __init__(
        self,
        pipeline_name,
        threshold,
        risk_exclusions,
        vulnerability_management_gateway,
        dict_args,
        secret_tool,
        config_tool,
        services,
    ):
        self.pipeline_name = pipeline_name
        self.threshold = threshold
        self.risk_exclusions = risk_exclusions
        self.vulnerability_management_gateway = vulnerability_management_gateway
        self.dict_args = dict_args
        self.secret_tool = secret_tool
        self.config_tool = config_tool
        self.services = services

    def process(self):
        if (self.pipeline_name in self.risk_exclusions.keys()) and (
            self.risk_exclusions[self.pipeline_name].get("THRESHOLD", None)
        ):
            base_threshold = self.risk_exclusions[self.pipeline_name]["THRESHOLD"]
        elif "BY_PATTERN_SEARCH" in self.risk_exclusions.keys():
            base_threshold = None
            for pattern, values in self.risk_exclusions["BY_PATTERN_SEARCH"].items():
                if re.match(pattern, self.pipeline_name):
                    base_threshold = values["THRESHOLD"]
                    break
            if base_threshold is None:
                base_threshold = self.threshold
        else:
            base_threshold = self.threshold

        quality_config = base_threshold.get(
            "QUALITY_VULNERABILITY_MANAGEMENT"
        )
        if quality_config:
            return self._apply_quality_vulnerability_management(
                quality_config, base_threshold
            )

        return base_threshold

    def _apply_quality_vulnerability_management(self, quality_config, base_threshold):
        """Apply dynamic threshold based on Product Type configuration"""

        product_type = self.vulnerability_management_gateway.get_product_type_pipeline(
            self.pipeline_name, self.dict_args, self.secret_tool, self.config_tool
        )

        if not product_type:
            return base_threshold

        pt_name = product_type.name
        apply_quality_pt = next(
            filter(
                lambda qapt: pt_name in qapt,
                quality_config["PTS"],
            ),
            None,
        )

        if not apply_quality_pt:
            return base_threshold

        pt_info = apply_quality_pt[pt_name]
        pt_apps = pt_info["APPS"]

        applies_to_pipeline = pt_apps == "ALL" or any(
            service in pt_apps for service in self.services
        )

        if not applies_to_pipeline:
            return base_threshold

        pt_profile = pt_info.get("PROFILE")
        if pt_profile and pt_profile in quality_config:
            profile_config = quality_config[pt_profile]
            return profile_config

        return base_threshold
