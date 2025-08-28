---
sidebar_position: 2
---

# Module Engine Dast

## Overview

The `engine_dast` module is responsible for orchestrating Dynamic Application Security Testing (DAST) within the DevSecOps Engine Tools platform. It automates the execution of DAST tools, processes scan configurations, manages authentication flows, and integrates results for further risk analysis and reporting.

## Main Responsibilities

- **DAST Orchestration:** Executes DAST tools (e.g., Nuclei) against APIs and web applications.
- **Configuration Management:** Loads and processes scan configurations from JSON files.
- **Authentication Handling:** Supports multiple authentication mechanisms (JWT, OAuth, client credentials) for API and web application testing.
- **Integration:** Connects with external systems and the core engine for configuration, secrets, and result management.
- **Result Processing:** Aggregates and normalizes findings for risk evaluation and reporting.

## Key Components

- `runner_dast_scan.py`: Main entry point for DAST scan orchestration.
- `entry_point_dast.py`: Initializes the DAST engine and triggers the scan process.
- `dast_scan.py`: Core use case for executing the scan, handling configuration, exclusions, and result aggregation.
- **Adapters:** Integrations for tools (Nuclei), authentication (JWT, OAuth), and HTTP clients.
- **Models:** Represent API/WebApp configurations and operations.

## Supported Tools and Features

- **Nuclei:** Main DAST tool for scanning APIs and web applications.
- **Authentication:** JWT, OAuth, and client credentials supported for authenticated scans.
- **Configurable Targets:** Supports both API and web application targets via JSON configuration.
- **Exclusions and Thresholds:** Handles exclusions and custom thresholds for findings.

## Example Usage

1. Prepare a JSON configuration file describing the API or web application, including authentication details and operations.
2. Run the DAST engine via the orchestrator, specifying the configuration file and tool.

```sh
devsecops-engine-tools \
    --platform_devops github \
    --remote_config_source github \
    --remote_config_repo my-org/devsecops-config \
    --module engine_dast \
    --tool nuclei \
    --dast_file_path path/to/config.json
```

## Extensibility

- New DAST tools or authentication methods can be added by extending the adapters and models.
- Integrations with additional reporting or risk management systems can be implemented via the infrastructure layer.

## Testing

- Unit tests are provided in the `test/` directory, covering orchestration logic and configuration parsing.

