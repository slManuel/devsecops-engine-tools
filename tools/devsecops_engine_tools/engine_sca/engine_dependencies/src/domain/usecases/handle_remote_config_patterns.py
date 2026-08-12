import re

from devsecops_engine_tools.engine_core.src.infrastructure.helpers.skip_policy import (
    applicable_exclusion,
    should_skip_remote_config,
)


class HandleRemoteConfigPatterns:
    def __init__(
        self,
        remote_config,
        exclusions,
        pipeline_name,
    ):
        self.remote_config = remote_config
        self.exclusions = exclusions
        self.pipeline_name = pipeline_name

    def ignore_analysis_pattern(self):
        """
        Handle analysis pattern.

        Return: bool: False -> not scan, True -> scan.
        """
        ignore = self.remote_config["IGNORE_ANALYSIS_PATTERN"]
        if re.match(ignore, self.pipeline_name, re.IGNORECASE):
            return False
        else:
            return True

    def skip_from_exclusion(self):
        """
        Handle skip tool.

        Return: bool: True -> skip tool, False -> not skip tool.
        """
        exclusion = applicable_exclusion(self.exclusions, self.pipeline_name)
        return should_skip_remote_config(exclusion)
