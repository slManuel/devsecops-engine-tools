---
sidebar_position: 4
---

# Module Engine Risk

## Overview

The `engine_risk` module is responsible for risk aggregation, filtering, and policy enforcement within the DevSecOps Engine Tools platform. It processes vulnerability findings, applies exclusions and thresholds, enriches data (e.g., with EPSS), and determines if the build should be broken based on risk policies.

## Main Responsibilities

- **Risk Aggregation:** Collects and processes findings from vulnerability management platforms.
- **Filtering:** Applies filters based on tags, age, and custom policies to exclude or prioritize findings.
- **Data Enrichment:** Integrates external data sources (e.g., EPSS) to enhance risk context.
- **Exclusions Management:** Applies exclusion rules from configuration and runtime environment.
- **Threshold Evaluation:** Checks if the number or severity of findings exceeds defined thresholds.
- **Policy Enforcement:** Decides if the build should fail based on risk and policy evaluation.

## Key Components

- `runner_engine_risk.py`: Main entry point for risk aggregation and policy enforcement.
- `entry_point_risk.py`: Initializes the risk engine and coordinates the workflow.
- **Use Cases:** Located in `src/domain/usecases/`, including:
	- `HandleFilters`: Applies filtering logic to findings.
	- `AddData`: Enriches findings with additional data (e.g., EPSS).
	- `GetExclusions`: Determines which findings should be excluded.
	- `CheckThreshold`: Evaluates if thresholds are exceeded.
	- `BreakBuild`: Enforces build-breaking policies.

## Example Usage

The risk engine is typically invoked as part of the overall DevSecOps pipeline, after findings have been collected from various scans:

```sh
devsecops-engine-tools \
    --platform_devops azure \
    --remote_config_source azure \
    --remote_config_repo my-org/devsecops-config \
    --module engine_risk
```

## Extensibility

- New filters, enrichment sources, or policy rules can be added by extending the use cases.
- Supports integration with various vulnerability management and CI/CD platforms.

## Testing

- Unit tests are provided in the `test/` directory, covering filtering, enrichment, and policy logic.
