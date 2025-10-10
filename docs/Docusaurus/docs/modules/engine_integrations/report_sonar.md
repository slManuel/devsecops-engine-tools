# Report Sonar

## Overview

The `report_sonar` integration provides comprehensive code quality and security reporting capabilities within the DevSecOps Engine Tools platform. This integration fetches quality metrics, security hotspots, and code coverage data from SonarQube instances, enabling centralized reporting and analysis of code quality across multiple projects and components.

## Configuration Structure

The module is configured through two main JSON files located in `example_remote_config_local/engine_integrations/report_sonar/`:

### ConfigTool.json

Main configuration file that defines SonarQube integration behavior and reporting parameters.

```json
{
  "IGNORE_SEARCH_PATTERN": ".*test.*",
  "TARGET_BRANCHES": ["trunk", "develop", "master"],
  "MAX_RETRIES_QUERY_SONAR": 5,
  "USE_BRANCH_PARAMETER": false,
  "USE_PULL_REQUEST_PARAMETER": ["proyect1", "proyect2"],
  "PIPELINE_COMPONENTS": {
    "EXAMPLE_MULTICOMPONENT_PIPELINE": [
      "component1",
      "component2",
      "component3",
      "component4",
      "component5"
    ]
  }
}
```

#### Configuration Parameters

##### Search and Filtering Configuration
- **IGNORE_SEARCH_PATTERN**: Regex pattern to exclude projects/components from SonarQube reporting (e.g., `".*test.*"` excludes test projects)
- **TARGET_BRANCHES**: Array of Git branch names that should trigger SonarQube report generation (e.g., `["trunk", "develop", "master"]`)

##### Query Configuration
- **MAX_RETRIES_QUERY_SONAR**: Maximum number of retry attempts for SonarQube API queries (e.g., `5` retries for reliability)
- **USE_BRANCH_PARAMETER**: Boolean flag to enable branch-specific SonarQube queries
- **USE_PULL_REQUEST_PARAMETER**: Array of project names that should use pull request-specific analysis (e.g., `["proyect1", "proyect2"]`)

##### Multi-component Pipeline Configuration
- **PIPELINE_COMPONENTS**: Mapping of pipeline names to their component arrays for multi-component projects:
  - Pipeline name as key (e.g., `"EXAMPLE_MULTICOMPONENT_PIPELINE"`)
  - Array of component names that belong to the pipeline
  - Enables consolidated reporting across multiple SonarQube projects

### Exclusions.json

Defines exclusion rules for pipelines and patterns to skip SonarQube reporting.

#### Structure
```json
{
  "PIPELINE_NAME": {
    "create_date": "18112023",
    "expired_date": "18032024",
    "hu": "0000000"
  },
  "BY_PATTERN_SEARCH": {
    ".*_MY_PIPELINE": {
      "create_date": "18112023",
      "expired_date": "18032024",
      "hu": "0000000"
    }
  }
}
```

#### Exclusion Types
- **Pipeline-specific**: Direct exclusions by pipeline name (e.g., `"PIPELINE_NAME"`)
- **BY_PATTERN_SEARCH**: Regex pattern-based exclusions for matching multiple pipelines

#### Exclusion Fields
Each exclusion entry contains:
- `create_date`: Date when exclusion was created (format: DDMMYYYY)
- `expired_date`: Expiration date for the exclusion (format: DDMMYYYY)
- `hu`: Human user identifier for audit trail

## Main Responsibilities

- **SonarQube Data Retrieval:** Fetches quality metrics, security issues, and code coverage from SonarQube instances
- **Multi-component Reporting:** Aggregates data from multiple SonarQube projects for comprehensive pipeline reporting
- **Branch-aware Analysis:** Processes reports based on specific Git branches and pull requests
- **Retry Logic:** Implements robust retry mechanisms for reliable SonarQube API interactions
- **Project Filtering:** Applies pattern-based filtering to exclude test projects and irrelevant components
- **Exclusion Management:** Manages pipeline and pattern-based exclusions with audit trail
- **Centralized Reporting:** Consolidates SonarQube data for enterprise-wide code quality visibility

## Key Components

- **SonarQube API Client:** Handles authentication and API interactions with SonarQube instances
- **Report Aggregator:** Combines data from multiple components and projects
- **Configuration Manager:** Processes exclusions and multi-component pipeline mappings
- **Retry Handler:** Manages API retry logic and error handling
- **Branch Processor:** Handles branch-specific and pull request-specific queries

## Supported Features

- **Multi-instance Support:** Connect to multiple SonarQube instances for reporting
- **Component Aggregation:** Consolidate metrics from multiple components in complex pipelines
- **Branch-specific Analysis:** Generate reports for specific branches or pull requests
- **Robust API Handling:** Retry logic and error handling for reliable data retrieval
- **Pattern-based Filtering:** Exclude test projects and development branches automatically
- **Pull Request Integration:** Special handling for pull request-based quality gates
- **Audit Trail:** Complete tracking of exclusions and reporting operations
- **Flexible Project Mapping:** Support for complex project structures and naming conventions

## Example Usage

```sh
devsecops-engine-tools-integrations \
    --platform_devops github \
    --remote_config_source github \
    --remote_config_repo my-org/devsecops-config \
    --integration report_sonar
```

## Configuration Guidelines

### Branch Configuration
1. Configure `TARGET_BRANCHES` to match your GitOps workflow and main development branches
2. Include production and staging branches for comprehensive quality tracking
3. Exclude feature branches to focus on main development lines
4. Consider environment-specific branch patterns for different quality gates

### Multi-component Setup
1. Map complex pipelines in `PIPELINE_COMPONENTS` to enable consolidated reporting
2. Use consistent component naming conventions across SonarQube projects
3. Group related services and libraries under the same pipeline for better visibility
4. Regular review and update of component mappings as architecture evolves

### Retry and Reliability Configuration
1. Set appropriate `MAX_RETRIES_QUERY_SONAR` based on SonarQube instance reliability
2. Consider network latency and SonarQube load when setting retry counts
3. Monitor retry patterns to identify SonarQube performance issues
4. Implement exponential backoff for retry strategies

### Pull Request Configuration
1. Configure `USE_PULL_REQUEST_PARAMETER` for projects requiring PR-specific analysis
2. Ensure SonarQube is configured for pull request decoration
3. Align with quality gate policies for PR blocking
4. Consider performance impact of PR analysis on large projects

### Pattern Configuration
1. Use `IGNORE_SEARCH_PATTERN` to exclude test, demo, and experimental projects
2. Include common test indicators (test, demo, poc, sandbox)
3. Regular review and update of exclusion patterns
4. Consider case sensitivity and internationalization in patterns

### Exclusion Management
1. Add pipeline-specific exclusions for special cases or legacy projects
2. Use pattern-based exclusions for scalable filtering of project families
3. Set appropriate expiration dates for temporary exclusions
4. Include audit information for compliance and tracking
5. Regular review and cleanup of expired exclusions

## Integration Patterns

### CI/CD Pipeline Integration
```yaml
# Example Jenkins Pipeline
pipeline {
    agent any
    stages {
        stage('SonarQube Report') {
            steps {
                script {
                    sh '''
                        devsecops-engine-tools \
                            --module report_sonar \
                            --project_key ${JOB_NAME} \
                            --branch ${BRANCH_NAME}
                    '''
                }
            }
        }
    }
}
```

## SonarQube Metrics Collected

### Quality Metrics
- Code coverage percentage and line coverage
- Duplicated lines and blocks
- Lines of code and technical debt
- Maintainability rating and reliability rating

### Security Metrics
- Security hotspots and vulnerabilities
- Security rating and security review rating
- OWASP Top 10 compliance metrics
- CWE (Common Weakness Enumeration) coverage

### Code Quality Metrics
- Bugs and code smells
- Cyclomatic complexity
- Cognitive complexity
- Quality gate status and conditions

## Troubleshooting

### Common Issues
1. **API Connection Failures**: Verify SonarQube instance availability and authentication
2. **Retry Exhaustion**: Increase `MAX_RETRIES_QUERY_SONAR` or investigate SonarQube performance
3. **Component Mapping Issues**: Verify component names match SonarQube project keys
4. **Branch Parameter Errors**: Ensure branch names match SonarQube analysis branches

### Monitoring and Alerting
- Monitor SonarQube API response times and success rates
- Track retry patterns and failure causes
- Alert on quality gate failures for target branches
- Monitor exclusion usage and expiration dates

### Performance Optimization
- Implement caching for frequently accessed SonarQube data
- Use parallel queries for multi-component pipelines
- Optimize query parameters to reduce API load
- Consider SonarQube database performance tuning

## Security Considerations

### Authentication and Authorization
- Use service accounts with minimal required SonarQube permissions
- Implement secure token management for SonarQube API access
- Regular rotation of authentication credentials
- Monitor API access patterns for unauthorized usage

### Data Privacy
- Ensure compliance with data protection regulations when collecting metrics
- Implement data retention policies for collected SonarQube data
- Consider data anonymization for sensitive projects
- Secure storage and transmission of quality metrics

## Extensibility

- Custom metrics collection from SonarQube plugins and extensions
- Integration with additional code quality platforms (CodeClimate, Codacy)
- Enhanced reporting formats and visualization capabilities
- Custom aggregation rules for complex organizational structures
- Integration with quality gate automation and enforcement systems

## Testing

- Unit tests validate configuration parsing and exclusion logic
- Integration tests verify SonarQube API connectivity and data retrieval
- End-to-end tests ensure accurate multi-component aggregation
- Performance tests validate retry logic and large dataset handling