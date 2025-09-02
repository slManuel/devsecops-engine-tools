# Module Engine Dependencies

## Overview

The `engine_dependencies` module is responsible for orchestrating Software Composition Analysis (SCA) for application dependencies within the DevSecOps Engine Tools platform. It automates the execution of dependency scanning tools, processes scan configurations, manages exclusions, and integrates results for further risk analysis and reporting.

## Main Responsibilities

- **Dependency SCA Orchestration:** Executes dependency scanning tools (Xray, Dependency-Check, Trivy) on application codebases.
- **Configuration Management:** Loads and processes scan configurations and exclusions from remote repositories.
- **Folder and File Discovery:** Identifies relevant folders/files for scanning based on patterns and configuration.
- **Exclusions Management:** Applies exclusion rules based on configuration and DevSecOps policy.
- **Result Processing:** Aggregates and normalizes findings for risk evaluation and reporting.
- **SBOM Generation:** Supports extraction and management of Software Bill of Materials (SBOM) for dependencies.

## Key Components

- `runner_dependencies_scan.py`: Main entry point for dependency scan orchestration.
- `entry_point_tool.py`: Initializes the dependency SCA engine and triggers the scan process.
- `dependencies_sca_scan.py`: Core use case for executing the scan, handling configuration, exclusions, and result aggregation.
- **Adapters:** Integrations for dependency scanning tools (Xray, Dependency-Check, Trivy) and SBOM management.

## Supported Tools and Features

- **Xray:** Scans dependencies for vulnerabilities and compliance issues.
- **Dependency-Check:** Detects known vulnerabilities in project dependencies.
- **Trivy:** Scans dependencies and generates SBOMs.
- **SBOM Support:** Extracts and manages SBOMs for dependencies.
- **Configurable Exclusions:** Supports exclusion of dependencies and custom ignore patterns.
- **Thresholds and Policies:** Handles custom thresholds and build-breaking policies.

## Example Usage

The dependency SCA engine is typically invoked as part of the overall DevSecOps pipeline, after code or dependency changes are detected:

```sh
devsecops-engine-tools \
	--platform_devops github \
	--remote_config_source github \
	--remote_config_repo my-org/devsecops-config \
	--module engine_dependencies \
	--tool trivy \
	--folder_path path/to/project
```

## Extensibility

- New dependency scanning tools or exclusion policies can be added by extending the adapters and use cases.
- Supports integration with various package managers and CI/CD platforms.

## Testing

- Unit tests are provided in the `test/` directory, covering orchestration logic, configuration parsing, and exclusion handling.