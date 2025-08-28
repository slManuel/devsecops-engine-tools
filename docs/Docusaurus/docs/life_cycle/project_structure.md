---
sidebar_position: 3
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Project Structure

**¿Why is it important?**

Documenting the project structure is crucial so that anyone, whether a new developer or a member of the technical team, can quickly understand how the code is organized. This facilitates collaboration, maintenance, and scaling of the software, as well as helping to identify common patterns and potential areas for improvement.

**¡What should it include?**

- **Overview of the File Structure:**
    - The DevSecOps Engine Tools project is structured according to a clean architecture, where each service is an independent module but follows common patterns.
    
    ```
    devsecops_engine_tools
    ├───engine_core -> Main module.
    |           test
    |           src
    |               applications
    |               deployment
    |               domain
    |                   model
    |                   usecases
    |               infraestructure
    |                   driven_adapters
    |                   entry_points
    |                   utils.
    |
    ├───engine_risk -> Vulnerability management plaform report.
    |           test
    |           src
    |               applications
    |               deployment
    |               domain
    |                   model
    |                   usecases
    |               infraestructure
    |                   driven_adapters
    |                   entry_points
    |                   utils.
    |
    ├───engine_dast -> DAST Practice
    |           test
    |           src
    |               applications
    |               deployment
    |               domain
    |                   model
    |                   usecases
    |               infraestructure
    |                   driven_adapters
    |                   entry_points
    |                   utils.
    |
    ├───engine_sast -> SAST Practices
    |           engine_iac -> Infrastructure as code
    |              src
    |               applications
    |               deployment
    |               domain
    |                   model
    |                   usecases
    |               infraestructure
    |                   driven_adapters
    |                   entry_points
    |                   utils.
    |           engine_secret -> Secret Scanning
    |              src
    |               applications
    |               deployment
    |               domain
    |                   model
    |                   usecases
    |               infraestructure
    |                   driven_adapters
    |                   entry_points
    |                   utils.
    |           engine_code -> Static Code Scanning
    |              src
    |               applications
    |               deployment
    |               domain
    |                   model
    |                   usecases
    |               infraestructure
    |                   driven_adapters
    |                   entry_points
    |                   utils.
    |
    ├───engine_sca -> SCA Practices
    |            engine_container -> Container Scanning
    |              src
    |               applications
    |               deployment
    |               domain
    |                   model
    |                   usecases
    |               infraestructure
    |                   driven_adapters
    |                   entry_points
    |                   utils.
    |            engine_dependencies -> Dependency Scanning
    |              src
    |               applications
    |               deployment
    |               domain
    |                   model
    |                   usecases
    |               infraestructure
    |                   driven_adapters
    |                   entry_points
    |                   utils.
    |
    ├───engine_integrations -> Tool integration module.
    |           test
    |           src
    |               applications
    |               domain
    |                   usecases
    |               infraestructure
    |                   entry_points
    |
    ├───engine_utilities -> Utilities transversal.
    |           azuredevops
    |           defect_dojo
    |           git_cli
    |           github
    |           input_validations
    |           sbom
    |           sonarqube -> report_sonar integration
    |           ssh
    |           utils
    ```
