# Module Engine Function

## Overview

The `engine_function` module orchestrates Software Composition Analysis (SCA) for serverless functions packaged as .zip (e.g., AWS Lambda and Azure Functions) within the DevSecOps Engine Tools platform. It automates the execution of Prisma Cloud’s twistcli for serverless code, loads scan configuration, applies exclusions and thresholds, and normalizes results for risk analysis and reporting.

## Main Responsibilities

- **Serverless SCA Orchestration:** Runs Prisma Cloud twistcli serverless scan over function ZIP artifacts.
- **Configuration Management:** Loads tool settings, thresholds, and policies from remote configuration (or local examples).
- **Artifact Discovery:** Finds *.zip function packages in the provided folder_path.
- **Exclusions & Thresholds:** Applies per-pipeline and global exclusions (Exclusions.json) and evaluates thresholds to support build-break decisions in the core.
- **Result Processing:** Parses twistcli output to extract vulnerability and compliance distributions and CVE tables.
- **CI/CD Integration:** Works with Azure DevOps/GitHub environments via predefined variables and messaging helpers.

## Key Components

- **src/applications/runner_function_scan.py**
Entry point used by the core to start the Function SCA workflow (parses args, delegates to the use case).

- **src/infrastructure/entry_points/entry_point_function.py**
Bootstraps the module and returns (findings, input_core) to the engine core.

- **src/domain/usecases/function_scan.py**
Core use case: loads config (ConfigTool.json), checks exclusions (Exclusions.json), prepares input, and dispatches the scan.

- **Adapters**

- **src/infrastructure/driven_adapters/prisma_cloud/prisma_cloud_manager_scan.py**
Wrapper around twistcli serverless scan (download, execution, stdout parsing).

- **src/infrastructure/driven_adapters/azure_devops/azure_devops.py**
Helper for Azure DevOps predefined variables, remote config URL composition, and pipeline messages.

## Supported Tools and Features

- **Prisma Cloud (twistcli):** Downloads twistcli from Prisma Console via API.
- **Scans function ZIP:** Detects Vulnerability distribution: total/critical/high/medium/low.
- **Configurable Exclusions:** Supports exclusion of vulnerabilities and custom ignore patterns.
- **Thresholds and Policies:** Handles custom thresholds and build-breaking policies.

## Example Usage

Typically invoked by the engine core in CI:

```sh
python tools/devsecops_engine_tools/engine_core/src/applications/runner_engine_core.py \
  --platform_devops azure \
  --remote_config_source azure \
  --remote_config_repo <your-remote-config-repo> \
  --module engine_function \
  --tool prisma \
  --folder_path path/to/functions_zip_dir \
  --use_secrets_manager false \
  --use_vulnerability_management false \
  --send_metrics false

```

## Extensibility

- Add new serverless scanners by implementing a new adapter under driven_adapters/<tool>/ and wiring it in function_scan.py.
- Extend result parsing (e.g., additional compliance frameworks) by enhancing the parser and mapping to the engine’s finding model.

## Testing

- Unit tests are provided in the `test/` directory, covering orchestration logic, configuration parsing, and exclusion handling.