# Module Engine Secret

## Overview

The `engine_secret` module is responsible for orchestrating secret scanning within the DevSecOps Engine Tools platform. It automates the execution of secret scanning tools, processes scan configurations, manages exclusions, and integrates results for further risk analysis and reporting.

## Main Responsibilities

- **Secret Scanning Orchestration:** Executes secret scanning tools (Trufflehog, Gitleaks) on source code and pull requests.
- **Configuration Management:** Loads and processes scan configurations and exclusions from remote repositories.
- **Pull Request Analysis:** Identifies and filters files changed in pull requests for targeted secret scanning.
- **Exclusions Management:** Applies exclusion rules based on configuration and DevSecOps policy.
- **Result Processing:** Aggregates and normalizes findings for risk evaluation and reporting.

## Key Components

- `runner_secret_scan.py`: Main entry point for secret scan orchestration.
- `entry_point_tool.py`: Initializes the secret scanning engine and triggers the scan process.
- `secret_scan.py`: Core use case for executing the scan, handling configuration, exclusions, and result aggregation.
- **Adapters:** Integrations for secret scanning tools (Trufflehog, Gitleaks) and Git operations.

## Supported Tools and Features

- **Trufflehog:** Scans for secrets in code repositories.
- **Gitleaks:** Detects hardcoded secrets and credentials in source code.
- **Pull Request Scanning:** Supports scanning only files changed in pull requests.
- **Configurable Exclusions:** Supports exclusion of files/folders and custom ignore patterns.
- **Thresholds and Policies:** Handles custom thresholds and build-breaking policies.

## Example Usage

The secret scanning engine is typically invoked as part of the overall DevSecOps pipeline, after code changes are detected:

```sh
devsecops-engine-tools \
	--platform_devops github \
	--remote_config_source github \
	--remote_config_repo my-org/devsecops-config \
	--module engine_secret \
	--tool gitleaks \
	--folder_path path/to/source
```

## Extensibility

- New secret scanning tools or exclusion policies can be added by extending the adapters and use cases.
- Supports integration with various version control and CI/CD platforms.

## Testing

- Unit tests are provided in the `test/` directory, covering orchestration logic, configuration parsing, and exclusion handling.