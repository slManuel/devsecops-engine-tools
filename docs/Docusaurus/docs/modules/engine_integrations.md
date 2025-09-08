---
sidebar_position: 3
---

# Module Engine Integrations

## Overview

The `engine_integrations` module enables the integration of DevSecOps Engine Tools with external systems and platforms, focusing on orchestrating and automating reporting and data exchange processes. It is designed to be extensible, allowing new integrations to be added as needed.

## Main Responsibilities

- **Integration Orchestration:** Manages the execution of integration workflows, such as reporting to external systems.
- **Configuration Management:** Loads integration and tool configuration from remote repositories.
- **Platform Integration:** Connects with DevOps platforms (Azure DevOps, GitHub, local), secrets managers, vulnerability management, and metrics systems.
- **Reporting:** Automates the generation and delivery of reports (e.g., SonarQube reports) to external platforms.

## Key Components

- `runner_engine_integrations.py`: Main entry point for running integrations via CLI.
- `entry_point_integrations.py`: Initializes the integration engine and triggers the appropriate workflow.
- `handle_integrations.py`: Core use case for executing the selected integration (e.g., SonarQube report, Copacetic patching).
- **Adapters:** Integrations for DevOps platforms, secrets management, vulnerability management, and metrics.

## Supported Integrations

- **report_sonar:** Automates the collection and reporting of SonarQube analysis results, integrating with vulnerability management and metrics systems.
- **copacetic:** Integrates with the Copacetic tool to automatically patch container images by fixing known vulnerabilities, applies security patches to container images.

## Example CLI Usage

### SonarQube Report Integration
```sh
devsecops-engine-tools-integrations \
	--integration report_sonar \
	--remote_config_repo my-org/devsecops-config \
	--platform_devops github \
	--use_secrets_manager true \
	--sonar_url https://sonarqube.example.com \
	--sonar_instance my-sonar-instance \
	--token_sonar <SONAR_TOKEN>
```

### Copacetic Container Patching Integration
```sh
devsecops-engine-tools-integrations \
	--integration copacetic \
	--remote_config_repo my-org/devsecops-config \
	--platform_devops github \
	--use_secrets_manager true \
	--image nginx:latest \
	--vulnerability_report /path/to/trivy-report.json \
	--patch_format trivy
```

## Extensibility

- New integrations can be added by implementing additional use cases and updating the CLI interface.
- Supports integration with a variety of DevOps, security, and reporting platforms.

## Testing

- Unit tests are provided in the `test/` directory, covering integration logic and CLI argument parsing.


