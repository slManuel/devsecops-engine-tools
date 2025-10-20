# Copacetic Integration

## Overview

The `copacetic` integration provides automated vulnerability patching capabilities for container images within the DevSecOps Engine Tools platform. Copacetic is a project from Microsoft that enables in-place patching of container images by applying OS and dependency updates without rebuilding the entire image from scratch.

## Configuration Structure

The module is configured through two main JSON files located in `example_remote_config_local/engine_integrations/copacetic/`:

### ConfigTool.json

Main configuration file that defines Copacetic execution behavior and BuildKit settings.

```json
{
  "VERSION": "0.11.1",
  "IGNORE_SEARCH_PATTERN": "(?i).*(?:test|demo|sample).*",
  "TARGET_BRANCHES": ["main", "master", "develop", "release"],
  "TIMEOUT": 1800,
  "DEFAULT_OUTPUT_SUFFIX": "-patched",
  "BUILDKIT_CONFIG": {
    "DEFAULT_ADDR": "docker-container://buildkit",
    "PROGRESS": "auto",
    "IGNORE_ERRORS": false
  }
}
```

#### Configuration Parameters

##### General Configuration
- **VERSION**: Copacetic version to use (e.g., `"0.11.1"`)
- **IGNORE_SEARCH_PATTERN**: Case-insensitive regex pattern to exclude images from patching (e.g., `"(?i).*(?:test|demo|sample).*"` ignores test images)
- **TARGET_BRANCHES**: Array of Git branch names that should trigger Copacetic patching (e.g., `["main", "master", "develop", "release"]`)
- **TIMEOUT**: Maximum time in seconds for patching operations (e.g., `1800` for 30 minutes)
- **DEFAULT_OUTPUT_SUFFIX**: Suffix appended to patched image names (e.g., `"-patched"`)

##### BuildKit Configuration
- **DEFAULT_ADDR**: BuildKit daemon address for container image operations (e.g., `"docker-container://buildkit"`)
- **PROGRESS**: Progress output format for build operations (`"auto"`, `"plain"`, `"tty"`)
- **IGNORE_ERRORS**: Boolean flag to control error handling during BuildKit operations

### Exclusions.json

Defines exclusion rules for pipelines and patterns to skip Copacetic processing.

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

- **Vulnerability Patching:** Automatically applies security patches to container images without full rebuilds
- **Image Management:** Manages patched image creation with configurable naming conventions
- **Branch-based Processing:** Selectively processes images based on Git branch triggers
- **BuildKit Integration:** Leverages BuildKit for efficient container image operations
- **Exclusion Management:** Applies exclusion rules to skip inappropriate images or pipelines
- **Timeout Management:** Controls execution time to prevent runaway patching operations

## Key Components

- **Copacetic Engine:** Core patching functionality using Microsoft Copacetic
- **BuildKit Integration:** Container image building and management
- **Configuration Manager:** Handles exclusions and processing rules
- **Image Processor:** Manages image identification and patching workflows

## Supported Features

- **In-place Patching:** Updates container images without rebuilding from Dockerfile
- **OS Package Updates:** Applies operating system security patches
- **Dependency Updates:** Updates vulnerable dependencies within images
- **Efficient Processing:** Minimal image layer changes for faster deployments
- **Branch-aware Processing:** Configurable branch triggers for patching operations
- **Pattern-based Filtering:** Regex-based image and pipeline exclusions
- **BuildKit Integration:** Advanced container building capabilities
- **Audit Trail:** Complete tracking of patching operations and exclusions

## Example Usage

```sh
devsecops-engine-tools-integrations \
    --platform_devops github \
    --remote_config_source github \
    --remote_config_repo devsecops-config \
    --integration engine_integrations \
    --image_to_patch myapp:v1.0.0
```

## Configuration Guidelines

### Version Management
1. Use stable Copacetic versions for production environments
2. Test new versions in development before promoting
3. Monitor Copacetic release notes for breaking changes
4. Consider version pinning for consistent behavior

### Branch Configuration
1. Configure `TARGET_BRANCHES` to match your GitOps workflow
2. Include main branches where patched images should be deployed
3. Exclude feature branches to avoid unnecessary patching
4. Consider environment-specific branch patterns

### Pattern Configuration
1. Use `IGNORE_SEARCH_PATTERN` to exclude test and development images
2. Configure case-insensitive patterns for flexibility
3. Include common test indicators (test, demo, sample, dev)
4. Regular review and update of exclusion patterns

### BuildKit Optimization
1. Configure appropriate `DEFAULT_ADDR` for your container environment
2. Use `"auto"` progress for most environments
3. Set `IGNORE_ERRORS` to `false` for strict error handling
4. Consider BuildKit caching strategies for performance

### Timeout Management
1. Set realistic `TIMEOUT` values based on image size and complexity
2. Consider network latency for registry operations
3. Monitor timeout patterns to identify performance issues
4. Adjust timeouts based on historical patching duration

### Exclusion Management
1. Add pipeline-specific exclusions for special cases
2. Use pattern-based exclusions for scalable filtering
3. Set appropriate expiration dates for temporary exclusions
4. Include audit information for compliance tracking
5. Regular review and cleanup of expired exclusions


## Security Considerations

### Image Integrity
- Verify patched image functionality before deployment
- Implement image signing for patched images
- Maintain audit trail of all patching operations
- Test patched images in staging environments

### Access Control
- Restrict Copacetic execution to authorized pipelines
- Implement proper registry access controls
- Use service accounts with minimal required permissions
- Monitor patching operations for unauthorized access

### Supply Chain Security
- Validate patch sources and integrity
- Implement security scanning of patched images
- Maintain provenance information for patched images
- Consider image attestation for compliance

## Troubleshooting

### Common Issues
1. **Timeout Errors**: Increase `TIMEOUT` value or optimize network connectivity
2. **BuildKit Failures**: Verify BuildKit daemon availability and configuration
3. **Pattern Exclusions**: Review regex patterns for unintended matches
4. **Branch Filtering**: Ensure branch names match `TARGET_BRANCHES` configuration

### Monitoring and Logging
- Monitor patching success rates and failure patterns
- Track patching duration for performance optimization
- Log exclusion decisions for audit purposes
- Alert on repeated patching failures

## Extensibility

- Custom patching rules can be implemented for specific image types
- Integration with additional vulnerability databases
- Support for custom BuildKit configurations and optimizations
- Enhanced exclusion logic for complex organizational requirements
- Integration with image signing and attestation workflows

## Testing

- Unit tests validate configuration parsing and exclusion logic
- Integration tests verify Copacetic execution and BuildKit integration
- End-to-end tests ensure patched images maintain functionality
- Performance tests validate timeout and efficiency optimizations