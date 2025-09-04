---
sidebar_position: 1
---

# Module Engine Core

## Overview

The `engine_core` module is the central orchestrator of the DevSecOps Engine Tools platform. It coordinates the execution of security scans, manages configuration, integrates with external systems, and processes results for reporting and risk management. The module is designed following Clean Architecture principles, ensuring separation of concerns and extensibility.

## Main Responsibilities

- **Orchestration:** Manages the workflow for running security tools (SAST, DAST, IaC, container, dependencies, secrets, risk).
- **Configuration Management:** Loads and applies configuration from remote repositories (Azure, GitHub, local).
- **Integration:** Connects with external platforms such as DefectDojo, cloud providers, artifact repositories, and CI/CD systems.
- **Result Processing:** Aggregates, normalizes, and processes scan results, including risk assessment and metrics reporting.
- **CLI Interface:** Provides a command-line interface for flexible execution and integration in pipelines.

## Key Components

- `runner_engine_core.py`: Main entry point for CLI execution and orchestration logic.
- `entry_point_core.py`: Initializes the engine, loads configuration, and triggers the appropriate use cases.
- **Use Cases:** Located in `src/domain/usecases/`, including:
	- `HandleScan`: Executes and processes security scans.
	- `HandleRisk`: Aggregates and evaluates risk based on findings.
	- `BreakBuild`: Determines if the build should fail based on policy.
	- `MetricsManager`: Handles metrics collection and reporting.

## Supported Modules and Tools

- **engine_iac:** IaC security (Checkov, KICS, Kubescape)
- **engine_secret:** Secret scanning (Trufflehog, Gitleaks)
- **engine_container:** Container scanning (Prisma, Trivy)
- **engine_dependencies:** Dependency scanning (Xray, Dependency-Check, Trivy)
- **engine_code:** Code scanning (Bearer)
- **engine_dast:** DAST scanning (Nuclei)
- **engine_risk:** Risk aggregation

## Example CLI Usage

```sh
devsecops-engine-tools \
	--platform_devops github \
	--remote_config_source github \
	--remote_config_repo my-org/devsecops-config \
	--module engine_container \
	--tool trivy \
	--image_to_scan myimage:latest
```

## Extensibility

- New tools and modules can be added by extending the adapters and use cases.
- Integrations with new platforms or reporting systems can be implemented via the infrastructure layer.

## Testing

- Unit tests are provided in the `test/` directory, covering core logic and CLI argument parsing.


