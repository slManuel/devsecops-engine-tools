# Module Engine Container

## Overview

The `engine_container` module is responsible for vulnerability scanning of container images within the DevSecOps Engine Tools platform. It automates the execution of container scanning tools, processes scan configurations, manages exclusions, and integrates results for further risk analysis and reporting.

## Main Responsibilities

- **Container SCA Orchestration:** Executes container scanning tools (Trivy, Prisma Cloud) on container images.
- **Configuration Management:** Loads and processes scan configurations and exclusions from remote repositories.
- **Image Discovery:** Identifies and manages container images to be scanned.
- **Exclusions Management:** Applies exclusion rules based on configuration and DevSecOps policy.
- **Result Processing:** Aggregates and normalizes findings for risk evaluation and reporting.
- **SBOM Generation:** Supports extraction and management of Software Bill of Materials (SBOM) for container images.

## Key Components

- `runner_container_scan.py`: Main entry point for container scan orchestration.
- `entry_point_tool.py`: Initializes the container SCA engine and triggers the scan process.
- `container_sca_scan.py`: Core use case for executing the scan, handling configuration, exclusions, and result aggregation.
- **Adapters:** Integrations for container scanning tools (Trivy, Prisma Cloud) and Docker image management.

## Supported Tools and Features

- **Trivy:** Scans container images for vulnerabilities and compliance issues.
- **Prisma Cloud:** Provides advanced container security scanning and policy enforcement.
- **SBOM Support:** Extracts and manages SBOMs for container images.
- **Configurable Exclusions:** Supports exclusion of images and custom ignore patterns.
- **Thresholds and Policies:** Handles custom thresholds and build-breaking policies.

## Example Usage

The container SCA engine is typically invoked as part of the overall DevSecOps pipeline, after container images are built or updated:

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

- New container scanning tools or exclusion policies can be added by extending the adapters and use cases.
- Supports integration with various container registries and CI/CD platforms.

## Testing

- Unit tests are provided in the `test/` directory, covering orchestration logic, configuration parsing, and exclusion handling.