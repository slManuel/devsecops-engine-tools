# Module Engine Iac

## Overview

The `engine_iac` module is responsible for orchestrating Infrastructure as Code (IaC) security scanning within the DevSecOps Engine Tools platform. It automates the execution of IaC security tools, processes scan configurations, manages exclusions, and integrates results for further risk analysis and reporting.

## Main Responsibilities

- **IaC Security Orchestration:** Executes IaC security tools (Checkov, KICS, Kubescape) on infrastructure code.
- **Configuration Management:** Loads and processes scan configurations and exclusions from remote repositories.
- **Folder and File Discovery:** Identifies relevant folders/files for scanning based on patterns and configuration.
- **Exclusions Management:** Applies exclusion rules based on configuration and DevSecOps policy.
- **Result Processing:** Aggregates and normalizes findings for risk evaluation and reporting.

## Key Components

- `runner_iac_scan.py`: Main entry point for IaC scan orchestration.
- `entry_point_tool.py`: Initializes the IaC engine and triggers the scan process.
- `iac_scan.py`: Core use case for executing the scan, handling configuration, exclusions, and result aggregation.
- **Adapters:** Integrations for IaC security tools (Checkov, KICS, Kubescape).

## Supported Tools and Features

- **Checkov:** Scans Terraform, CloudFormation, Kubernetes, and more for security misconfigurations.
- **KICS:** Scans IaC files for vulnerabilities and compliance issues.
- **Kubescape:** Focused on Kubernetes security scanning.
- **Configurable Exclusions:** Supports exclusion of files/folders and custom ignore patterns.
- **Thresholds and Policies:** Handles custom thresholds and build-breaking policies.

## Example Usage

The IaC engine is typically invoked as part of the overall DevSecOps pipeline, after infrastructure code changes are detected:

```sh
devsecops-engine-tools \
	--platform_devops github \
	--remote_config_source github \
	--remote_config_repo my-org/devsecops-config \
	--module engine_iac \
	--tool checkov \
	--folder_path path/to/iac
```

## Extensibility

- New IaC security tools or exclusion policies can be added by extending the adapters and use cases.
- Supports integration with various version control and CI/CD platforms.

## Testing

- Unit tests are provided in the `test/` directory, covering orchestration logic, configuration parsing, and exclusion handling.