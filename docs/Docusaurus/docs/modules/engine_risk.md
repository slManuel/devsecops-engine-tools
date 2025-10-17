---
sidebar_position: 4
---

# Module Engine Risk

## Overview

The `engine_risk` module is responsible for risk aggregation, filtering, and policy enforcement within the DevSecOps Engine Tools platform. It processes vulnerability findings, applies exclusions and thresholds, enriches data (e.g., with EPSS), and determines if the build should be broken based on risk policies.

## Configuration Structure

The module is configured through two main JSON files located in `example_remote_config_local/engine_risk/`:

### ConfigTool.json

Main configuration file that defines risk analysis behavior, scoring weights, and policy enforcement rules.

```json
{
  "MESSAGE_INFO": "Custom message",
  "IGNORE_ANALYSIS_PATTERN": "(.*_test|test_.*)",
  "COUNTRY_HOLIDAYS": "CO",
  "HANDLE_SERVICE_NAME": {
    "ENABLED": "false",
    "CHECK_ENDING": ["_ending1", "_ending2"],
    "REGEX_GET_SERVICE_CODE": "[^_]+",
    "REGEX_GET_WORDS": "[_-]",
    "MIN_WORD_LENGTH": 3,
    "MIN_WORD_AMOUNT": 2,
    "REGEX_CHECK_WORDS": "(a^)",
    "ADD_SERVICES": ["{service_code}-custom_service", "custom_service"]
  },
  "PARENT_ANALYSIS": {
    "ENABLED": "false",
    "REGEX_GET_PARENT": "^.*?_parent_id"
  },
  "EXCLUSIONS_PATHS": {
    "engine_code": "engine_sast/engine_code/Exclusions.json",
    "engine_iac": "engine_sast/engine_iac/Exclusions.json",
    "engine_secret": "engine_sast/engine_secret/Exclusions.json",
    "engine_container": "engine_sca/engine_container/Exclusions.json",
    "engine_dependencies": "engine_sca/engine_dependencies/Exclusions.json"
  },
  "WEIGHTS": {
    "severity": {
      "critical": 10,
      "high": 5,
      "medium": 3,
      "low": 1
    },
    "tags": {
      "engine_iac": 0,
      "engine_secret": 0,
      "engine_container": 0,
      "engine_dependencies": 0
    },
    "age": 0.0333,
    "max_age": 12,
    "epss_score": 100
  },
  "RUNTIME_TAG_EXCLUSION_DAYS": {
    "ENABLED": false,
    "ERROR_ON_FAILED": false
  },
  "TAG_EXCLUSION_DAYS": {
    "tag1": 10,
    "tag2": 20
  },
  "TAG_BLACKLIST_EXCLUSION_DAYS": {
    "tag3": 5,
    "tag4": 0
  },
  "THRESHOLD": {
    "REMEDIATION_RATE": {
      "1": 0,
      "5": 30,
      "10": 50,
      "other": 70
    },
    "RISK_SCORE": 10
  }
}
```

#### Configuration Parameters

##### General Configuration
- **MESSAGE_INFO**: Custom informational message for risk analysis execution
- **IGNORE_ANALYSIS_PATTERN**: Regex pattern to exclude repositories/components from analysis (e.g., `"(.*_test|test_.*)"` excludes test repositories)
- **COUNTRY_HOLIDAYS**: Country code for holiday calculations affecting remediation timelines (e.g., `"CO"` for Colombia)

##### Service Name Handling
- **HANDLE_SERVICE_NAME.ENABLED**: Boolean flag to enable/disable service name processing
- **CHECK_ENDING**: Array of service name endings to validate (e.g., `["_ending1", "_ending2"]`)
- **REGEX_GET_SERVICE_CODE**: Regex pattern to extract service code from names
- **REGEX_GET_WORDS**: Regex pattern to split service names into words
- **MIN_WORD_LENGTH**: Minimum length for valid words in service names
- **MIN_WORD_AMOUNT**: Minimum number of words required in service names
- **REGEX_CHECK_WORDS**: Regex pattern to validate extracted words
- **ADD_SERVICES**: Array of additional services to include in analysis with variable substitution

##### Parent Analysis Configuration
- **PARENT_ANALYSIS.ENABLED**: Boolean flag to enable hierarchical analysis
- **REGEX_GET_PARENT**: Regex pattern to extract parent identifier from service names

##### Exclusions Path Mapping
- **EXCLUSIONS_PATHS**: Mapping of engine modules to their exclusion file paths:
  - `engine_code`: Path to SAST exclusions
  - `engine_iac`: Path to Infrastructure as Code exclusions
  - `engine_secret`: Path to secret scanning exclusions
  - `engine_container`: Path to container scanning exclusions
  - `engine_dependencies`: Path to dependency scanning exclusions

##### Risk Scoring Weights
**Severity Weights:**
- `critical`: Weight value 10 (highest impact)
- `high`: Weight value 5
- `medium`: Weight value 3
- `low`: Weight value 1 (lowest impact)

**Engine Tag Weights:**
- `engine_iac`: Weight 0 (Infrastructure as Code findings)
- `engine_secret`: Weight 0 (Secret scanning findings)
- `engine_container`: Weight 0 (Container scanning findings)
- `engine_dependencies`: Weight 0 (Dependency scanning findings)

**Time-based Scoring:**
- `age`: Age multiplier factor (0.0333 per month)
- `max_age`: Maximum age in months for scoring calculation (12 months)
- `epss_score`: EPSS (Exploit Prediction Scoring System) weight multiplier (100)

##### Tag-based Exclusions
- **RUNTIME_TAG_EXCLUSION_DAYS**: Configuration for runtime tag exclusions:
  - `ENABLED`: Boolean flag to enable runtime tag processing
  - `ERROR_ON_FAILED`: Boolean flag to error if tag exclusion processing fails
- **TAG_EXCLUSION_DAYS**: Days to exclude findings based on tags:
  - `tag1`: 10 days exclusion
  - `tag2`: 20 days exclusion
- **TAG_BLACKLIST_EXCLUSION_DAYS**: Blacklist-based tag exclusions:
  - `tag3`: 5 days exclusion
  - `tag4`: 0 days (immediate processing)

##### Threshold Configuration
- **REMEDIATION_RATE**: Expected remediation rates based on vulnerability count:
  - `1`: 0% (single vulnerability - immediate fix)
  - `5`: 30% minimum remediation rate
  - `10`: 50% minimum remediation rate
  - `other`: 70% minimum remediation rate for larger counts
- **RISK_SCORE**: Maximum acceptable risk score threshold (10)

### Exclusions.json

Defines exclusion rules for specific risk findings across different scopes.

#### Structure
```json
{
  "All": {
    "RISK": [
      {
        "id": "XRAY-ID",
        "cve_id": "CVE-2023-35116",
        "where": "all",
        "create_date": "24012023",
        "expired_date": "22092023",
        "hu": "345345",
        "reason": "False Positive"
      },
      {
        "id": "CKV_K8S_ID",
        "where": "all",
        "cve_id": "N.A",
        "create_date": "05122023",
        "expired_date": "01082024",
        "severity": "critical",
        "hu": "345345"
      }
    ]
  },
  "Pipeline_Test": {
    "RISK": [
      {
        "id": "CVE-ID",
        "cve_id": "CVE-ID",
        "expired_date": "21092024",
        "create_date": "24012023",
        "hu": "345345"
      }
    ]
  }
}
```

#### Exclusion Types
- **All**: Global exclusions applied to all pipelines and repositories
- **Pipeline-specific**: Exclusions for specific pipelines (e.g., `"Pipeline_Test"`)
- **RISK**: Risk-specific exclusions for vulnerability findings

#### Exclusion Fields
Each exclusion entry contains:
- `id`: Tool-specific vulnerability or finding identifier
- `cve_id`: CVE identifier when applicable (`"N.A"` for non-CVE findings)
- `where`: Scope of exclusion (`"all"` for global or specific component/path)
- `create_date`: Date when exclusion was created (format: DDMMYYYY)
- `expired_date`: Expiration date for the exclusion (format: DDMMYYYY)
- `severity`: Original severity level of the excluded finding (optional)
- `hu`: Human user identifier for audit trail
- `reason`: Justification for exclusion (e.g., `"False Positive"`, `"Business Risk Accepted"`)

## Main Responsibilities

- **Risk Aggregation:** Collects and processes findings from vulnerability management platforms with weighted scoring
- **Filtering:** Applies filters based on tags, age, and custom policies to exclude or prioritize findings
- **Data Enrichment:** Integrates external data sources (EPSS scores) to enhance risk context and scoring
- **Exclusions Management:** Applies exclusion rules from configuration and runtime environment with audit trail
- **Threshold Evaluation:** Checks if the number, severity, or risk score of findings exceeds defined thresholds
- **Policy Enforcement:** Decides if the build should fail based on risk and policy evaluation
- **Service Management:** Handles service name normalization and hierarchical analysis
- **Time-based Analysis:** Incorporates vulnerability age and remediation timelines in risk calculations
- **Holiday-aware Processing:** Considers country-specific holidays in remediation deadline calculations

## Key Components

- `runner_engine_risk.py`: Main entry point for risk aggregation and policy enforcement
- `entry_point_risk.py`: Initializes the risk engine and coordinates the workflow
- **Use Cases:** Located in `src/domain/usecases/`, including:
	- `HandleFilters`: Applies filtering logic to findings with tag-based exclusions
	- `AddData`: Enriches findings with additional data (EPSS scores, age calculations)
	- `GetExclusions`: Determines which findings should be excluded based on configuration
	- `CheckThreshold`: Evaluates if thresholds are exceeded using weighted scoring
	- `BreakBuild`: Enforces build-breaking policies based on risk assessment
	- `ServiceNameHandler`: Processes and normalizes service names
	- `ParentAnalysis`: Handles hierarchical service analysis

## Supported Features

- **Multi-engine Integration:** Aggregates findings from SAST, SCA, DAST, and IAC engines
- **Advanced Scoring:** Weighted risk scoring based on severity, age, EPSS scores, and engine tags
- **Time-aware Analysis:** Holiday-aware remediation timeline calculations
- **Tag-based Filtering:** Configurable exclusions based on finding tags and age
- **Service Hierarchy:** Support for parent-child service relationships
- **EPSS Integration:** Exploit Prediction Scoring System integration for enhanced risk assessment
- **Flexible Thresholds:** Configurable remediation rate expectations based on vulnerability count
- **Audit Trail:** Complete exclusion tracking with creation dates, expiration, and user identification

## Example Usage

The risk engine is typically invoked as part of the overall DevSecOps pipeline, after findings have been collected from various scans:

```sh
devsecops-engine-tools \
    --platform_devops azure \
    --remote_config_source azure \
    --remote_config_repo devsecops-config \
    --module engine_risk
```

## Configuration Guidelines

### Risk Scoring Configuration
1. **Severity Weights**: Adjust weights based on organizational risk tolerance
2. **Engine Tag Weights**: Configure different weights for different scanning engines
3. **Age Factor**: Tune age multiplier based on organizational patching timelines
4. **EPSS Integration**: Leverage EPSS scores for prioritizing actively exploited vulnerabilities

### Service Management
1. Enable `HANDLE_SERVICE_NAME` for normalized service identification
2. Configure regex patterns to match organizational naming conventions
3. Use `ADD_SERVICES` for including custom or derived service names
4. Enable `PARENT_ANALYSIS` for microservice architectures with hierarchical relationships

### Threshold Management
1. Set realistic `REMEDIATION_RATE` expectations based on team capacity
2. Adjust `RISK_SCORE` threshold based on organizational risk appetite
3. Use different thresholds for different environments (dev vs prod)
4. Monitor threshold effectiveness and adjust based on historical data

### Tag-based Exclusions
1. Configure `TAG_EXCLUSION_DAYS` for temporary exclusions during remediation
2. Use `TAG_BLACKLIST_EXCLUSION_DAYS` for permanent or priority-based exclusions
3. Enable `RUNTIME_TAG_EXCLUSION_DAYS` for dynamic tag processing
4. Regular review and cleanup of tag-based exclusions

### Exclusion Management
1. Add exclusions with specific finding IDs when possible
2. Include CVE identifiers for vulnerability tracking
3. Set realistic expiration dates for temporary exclusions
4. Document business justification in the `reason` field
5. Use pipeline-specific exclusions instead of global ones when appropriate

## Extensibility

- New filters, enrichment sources, or policy rules can be added by extending the use cases
- Custom scoring algorithms can be implemented for specialized risk assessments
- Additional data sources (threat intelligence, business context) can be integrated
- Service naming and hierarchy logic can be customized for different organizational structures
- Supports integration with various vulnerability management and CI/CD platforms
- Holiday calendars can be extended for different countries and regions

## Testing

- Unit tests are provided in the `test/` directory, covering filtering, enrichment, and policy logic
- Integration tests validate scoring algorithms and threshold evaluation
- Service name processing and parent analysis testing included
- Risk aggregation and exclusion processing tests ensure accurate risk assessment
