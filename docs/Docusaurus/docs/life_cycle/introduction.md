---
sidebar_position: 1
---

# Introduction

## DevSecOps Engine Tools

**DevSecOps Engine Tools** is a library that automates, centralizes, and facilitates security, compliance, and quality management throughout the software development lifecycle. The ecosystem consists of modules and utilities that enable development, security, and operations teams to:

- Orchestrate and automate security scans (SAST, SCA, DAST, IaC) on code, containers, artifacts, and environments.
- Generate and manage SBOMs (Software Bill of Materials) for traceability and regulatory compliance.
- Integrate and consolidate results from different analysis engines, generating unified and actionable reports.
- Facilitate integration with CI/CD pipelines and artifact repositories.
- Provide metrics, alerts, and dashboards for decision-making and continuous improvement.

### What it does

#### Main components:

- **Processing and normalization:** Standardizes and transforms the data received through batch and streaming flows, ensuring the consistency and quality of the information.
- **Flow orchestrator:** Coordinates task execution, integration with other systems, and event management to keep vulnerability and compliance information up to date.
- **Integration with ASPM:** Sends processed results to a centralized vulnerability and compliance management platform and synchronizes statuses with vendor databases.
- **SBOM and artifact management:** Enables the generation, storage, and querying of SBOMs, facilitating the traceability of components and dependencies in the analyzed artifacts.


### ¿What problem does it solve?

DevSecOps Engine Tools solves the challenge of fragmentation and dispersion of security information by centralizing and standardizing vulnerability and compliance data from various sources. Thanks to its reactive architecture and efficient processing, it allows you to:

- Unify vulnerability and compliance management
- Automate the flow of information between external systems and the centralized platform
- Provide processed data ready for analysis, remediation, and auditing

This documentation is intended for developers, security engineers, and system administrators who need to understand, maintain, or extend the functionality of DevSecOps Engine Tools.