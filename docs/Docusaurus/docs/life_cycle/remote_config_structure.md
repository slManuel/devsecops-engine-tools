---
sidebar_position: 2
---

# Structure Remote Config

[example_remote_config_local](https://github.com/bancolombia/devsecops-engine-tools/blob/trunk/example_remote_config_local/)
```bash
📦Remote_Config
   ┣ 📂engine_core
   ┃ ┗ 📜ConfigTool.json
   ┣ 📂engine_dast
   ┃ ┗ 📜ConfigTool.json
   ┃ ┗ 📜Exclusions.json
   ┣ 📂engine_integrations
   ┃ ┗ 📂report_sonar
   ┃   ┗ 📜ConfigTool.json
   ┃   ┗ 📜Exclusions.json
   ┃ ┗ 📂copacetic
   ┃   ┗ 📜ConfigTool.json
   ┃   ┗ 📜Exclusions.json
   ┣ 📂engine_risk
   ┃ ┗ 📜ConfigTool.json
   ┃ ┗ 📜Exclusions.json
   ┣ 📂engine_sast
   ┃ ┗ 📂engine_iac
   ┃   ┗ 📜ConfigTool.json
   ┃   ┗ 📜Exclusions.json
   ┃ ┗ 📂engine_secret
   ┃   ┗ 📜ConfigTool.json
   ┃ ┗ 📂engine_code
   ┃   ┗ 📜ConfigTool.json
   ┃   ┗ 📜Exclusions.json
   ┣ 📂engine_sca
   ┃ ┗ 📂engine_container
   ┃   ┗ 📜ConfigTool.json
   ┃   ┗ 📜Exclusions.json
   ┃ ┗ 📂engine_dependencies
   ┃   ┗ 📜ConfigTool.json
   ┃   ┗ 📜Exclusions.json
   ┃ ┗ 📂engine_function
   ┃   ┗ 📜ConfigTool.json
   ┃   ┗ 📜Exclusions.json
```

## **engine_core**

Module is responsible to handle core configurations

For more information about structure remote config for this module, visit [engine core](../modules/engine_core.md)

> /engine_core/ConfigTool.json
```json
{
    "BANNER": "DevSecOps Engine Tools",
    "WARNING_RELEASE": false,
    "SECRET_MANAGER": {
        "AWS": {
            "SECRET_NAME": "",
            "USE_ROLE": false,
            "ROLE_ARN": "",
            "REGION_NAME": ""
        }
    },
    "VULNERABILITY_MANAGER": {
        "BRANCH_FILTER": [
            "trunk",
            "main"
        ],
        "DEFECT_DOJO": {
            "HOST_DEFECT_DOJO": "",
            "PRINT_DOMAIN": "",
            "LIMITS_QUERY": 100,
            "MAX_RETRIES_QUERY": 5,
            "TOOL_SCM_MAPPING": {
                "DEFAULT": 2,
                "TFSGIT": 2,
                "GITHUB": 3
            },
            "TOOL_SONAR_MAPPING": {
                "DEFAULT": 4,
                "SONAR_INSTANCE_ONE": 4,
                "SONAR_INSTANCE_TWO": 5
            },
            "TOOL_SLA_MAPPING": {
                "DEFAULT": 1,
                "ORPHAN": 4
            },
            "REIMPORT_SCAN": false,
            "CMDB": {
                "USE_CMDB": false,
                "HOST_CMDB": "",
                "GENERATE_AUTH_CMDB": false,
                "AUTH_CMDB_REQUEST_REPONSE": {
                    "URL": "",
                    "HEADERS": {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    "METHOD": "POST",
                    "PARAMS": "username=test&password=#{passwordvalue}#",
                    "RESPONSE": null
                },
                "REGEX_EXPRESSION_CMDB": "",
                "CMDB_MAPPING_PATH": "",
                "CMDB_MAPPING": {
                    "PRODUCT_TYPE_NAME": "",
                    "PRODUCT_NAME": "",
                    "TAG_PRODUCT": "",
                    "PRODUCT_DESCRIPTION": "",
                    "CODIGO_APP": ""
                },
                "CMDB_REQUEST_RESPONSE": {
                    "HEADERS": {
                        "Content-Type": "application/json",
                        "Api-Key": "tokenvalue"
                    },
                    "METHOD": "GET|POST",
                    "PARAMS": {
                        "appCode": "codappvalue"
                    },
                    "BODY": {
                        "appCode": "codappvalue"
                    },
                    "RESPONSE": [0]
                }
            }
        }
    },
    "METRICS_MANAGER": {
        "AWS": {
            "BUCKET": "",
            "TYPE_FORMAT_BUCKET_FILE": "parquet|json",
            "PATH_BUCKET": "engine_tools",
            "USE_ROLE": false,
            "ROLE_ARN": "",
            "REGION_NAME": ""
        }
    },
    "SBOM_MANAGER": {
        "ENABLED": true,
        "TOOL": "SYFT|CDXGEN",
        "BRANCH_FILTER": [],
        "SYFT": {
            "SYFT_VERSION": "1.17.0",
            "OUTPUT_FORMAT": "cyclonedx-json"
        },
        "CDXGEN": {
            "CDXGEN_VERSION": "11.7.0",
            "OUTPUT_FORMAT": "cyclonedx-json",
            "SLIM_BINARY": true,
            "EXCLUDE_TYPES": ["jar"],
            "EXCLUDE_PATHS": ["**/test/**"],
            "RECURSE": true,
            "DEBUG_PIPELINES": ["pipeline_name1", "pipeline_name2"]
        }
    },
    "ENGINE_IAC": {
        "ENABLED": true,
        "TOOL": "CHECKOV|KUBESCAPE|KICS"
    },
    "ENGINE_CONTAINER": {
        "ENABLED": true,
        "TOOL": "PRISMA|TRIVY"
    },
    "ENGINE_DAST": {
        "ENABLED": true,
        "TOOL": "NUCLEI",
        "EXTRA_TOOLS": ["JWT"]
    },
    "ENGINE_SECRET": {
        "ENABLED": true,
        "TOOL": "TRUFFLEHOG|GITLEAKS"
    },
    "ENGINE_DEPENDENCIES": {
        "ENABLED": true,
        "TOOL": "XRAY|DEPENDENCY_CHECK|TRIVY"
    },
    "ENGINE_CODE": {
        "ENABLED": true,
        "TOOL": "BEARER|KIUWAN"
    },
    "ENGINE_RISK": {
        "ENABLED": false
    },
    "ENGINE_FUNCTION": {
        "ENABLED": true,
        "TOOL": "PRISMA"
    },
    "REPORT_SONAR": {
        "ENABLED": true
    }
}
```

- **BANNER**: Application banner
- **WARNING_RELEASE**: warning in stage release break build
- **SECRET_MANAGER**: Driven adapter configuration for secrets manager
    - **AWS**
        - SECRET_NAME: secret name
        - USE_ROLE: use AWS role
        - ROLE_ARN: ARN of the assumed role with permissions over this resource
        - REGION_NAME: AWS region name

- **VULNERABILITY_MANAGER**: Driven adapter configuration for vulnerability manager
    - **BRANCH_FILTER**: Branch filter where the tool will send reports to the Vulnerability Manager.
        - feature/migration_open -> migration_open
        - PR -> [ID-PR]/merge
    - **DEFECT_DOJO**
        - HOST_DEFECT_DOJO: defect dojo host
        - PRINT_DOMAIN: Dominio to print
        - LIMITS_QUERY: Query limit for platform queries.
        - MAX_RETRIES_QUERY: Maximum number of retry attempts for queries to the platform
        - **TOOL_SCM_MAPPING**: Mapping between the source code management (SCM) tool and its corresponding identifier in DefectDojo.  
            - **DEFAULT**: Default SCM tool identifier.
            - **TFSGIT**: Identifier for Azure DevOps (TFS Git) repositories.
            - **GITHUB**: Identifier for GitHub repositories.

            Example:
            ```json
            "TOOL_SCM_MAPPING": {
                    "DEFAULT": 2,
                    "TFSGIT": 2,
                    "GITHUB": 3
            }
            ```
        - **TOOL_SONAR_MAPPING**: Mapping between SonarQube instances and their corresponding identifiers in DefectDojo.
            - **DEFAULT**: Default SonarQube instance identifier.
            - **SONAR_INSTANCE_ONE**: Identifier for the first SonarQube instance.
            - **SONAR_INSTANCE_TWO**: Identifier for the second SonarQube instance.

            Example:
            ```json
            "TOOL_SONAR_MAPPING": {
                "DEFAULT": 4,
                "SONAR_INSTANCE_ONE": 4,
                "SONAR_INSTANCE_TWO": 5
            }
            ```  
        - **TOOL_SLA_MAPPING**: Mapping between the SLA (Service Level Agreement) types and their corresponding identifiers in DefectDojo.
            - **DEFAULT**: Default SLA identifier.
            - **ORPHAN**: Identifier for orphaned findings or items without a specific SLA.

            Example:
            ```json
            "TOOL_SLA_MAPPING": {
                "DEFAULT": 1,
                "ORPHAN": 4
            }
            ```  
        - **REIMPORT_SCAN**: Boolean value that determines whether the scan results should be re-imported into DefectDojo. 
            - If set to `true`, the tool will attempt to re-import scan results, updating the same test.  
            - If set to `false`, each scan will be imported as a new test.  
        - **CMDB**: Configuration for the integration with the Configuration Management Database (CMDB).
            - **USE_CMDB**: Boolean value indicating whether to use CMDB integration (`true` or `false`).
            - **HOST_CMDB**: URL endpoint for the CMDB API.
            - **GENERATE_AUTH_CMDB**: Boolean value to enable or disable authentication request for the CMDB.
            - **AUTH_CMDB_REQUEST_REPONSE**: Object containing authentication request details if `GENERATE_AUTH_CMDB` is enabled.
                - **URL**: Authentication endpoint.
                - **HEADERS**: Headers required for the authentication request.
                - **METHOD**: HTTP method for the authentication request (e.g., `POST`).
                - **PARAMS**: Parameters for the authentication request.
                - **RESPONSE**: Expected response or token field.
            - **REGEX_EXPRESSION_CMDB**: Regular expression used to extract or filter data from the CMDB response.
            - **CMDB_MAPPING_PATH**: Path to the mapping file for product types or other mappings.
            - **CMDB_MAPPING**: Object mapping CMDB fields to DefectDojo fields.
                - **PRODUCT_TYPE_NAME**: Field name in CMDB for the product type.
                - **PRODUCT_NAME**: Field name in CMDB for the product name.
                - **TAG_PRODUCT**: Field name in CMDB for the product tag.
                - **PRODUCT_DESCRIPTION**: Field name in CMDB for the product description.
                - **CODIGO_APP**: Field name in CMDB for the application code.
            - **CMDB_REQUEST_RESPONSE**: Object containing the request and response configuration for querying the CMDB.
                - **HEADERS**: Headers required for the CMDB query.
                - **METHOD**: HTTP method for the CMDB query (`GET` or `POST`).
                - **PARAMS**: Parameters for the CMDB query (used for `GET`).
                - **BODY**: Body for the CMDB query (used for `POST`).
                - **RESPONSE**: Path or keys to extract the relevant data from the CMDB response.

        This section allows you to configure how the vulnerability management module interacts with your organization's CMDB, including authentication, data extraction, and field mapping, to ensure seamless integration and accurate data synchronization.

- **METRICS_MANAGER**: Driven adapter configuration for metrics manager
    - **AWS**
        - BUCKET: bucket where the metrics JSON will be sent
        - USE_ROLE: use AWS role
        - ROLE_ARN: ARN of the assumed role with permissions over this resource
        - REGION_NAME: AWS region name

- **ENGINE_IAC**: Configuration for the engine_iac tool
    - ENABLED: true or false
    - TOOL: CHECKOV |KUBESCAPE | KICS

- **ENGINE_CONTAINER**: Configuration for the engine_container tool
    - ENABLED: true or false
    - TOOL: PRISMA | TRIVY

- **ENGINE_DAST**: Configuration for the engine_dast tool
    - ENABLED: true or false
    - TOOL: NUCLEI

- **ENGINE_SECRET**: Configuration for the engine_secret tool
    - ENABLED: true or false
    - TOOL: TRUFFLEHOG | GITLEAKS

- **ENGINE_CODE**: Configuration for the engine_code tool
    - ENABLED: true or false
    - TOOL: BEARER

- **ENGINE_DEPENDENCIES**: Configuration for the engine_dependencies tool
    - ENABLED: true or false
    - TOOL: XRAY | DEPENDENCY_CHECK | TRIVY

- **ENGINE_RISK**: Configuration for the engine_risk tool
    - ENABLED: true or false

- **REPORT_SONAR**: Configuration for the report_sonar tool
    - ENABLED: true or false

- **ENGINE_FUNTION**: Configuration for the engine_function tool
    - ENABLED: true or false
    - TOOL: PRISMA


### Use Cases CMDB for vulnerability management

Initially, we need to know that the DevSecOps engine tools include a module for connecting to a vulnerability centralizer (DefectDojo). As a primary requirement for using this module, it must be considered whether a CMDB will be used or not. This is configurable through the remote config located in the [engine_core](https://github.com/bancolombia/devsecops-engine-tools/blob/trunk/example_remote_config_local/engine_core/ConfigTool.json). Below, examples of the two possible cases will be provided:

#### Using CMDB:
Let's suppose the CMDB response is as follows:
```json
{
    "count": 2,
    "value": [
        {
            "ApplicationCode": "code1-app",
            "ApplicationName": "Example Application Name 1",
            "ApplicationType": "Example Application type 1",
            "ApplicationTag": "Example Application tag 1",
            "ApplicationDescription": "Example Application description 1",
            "Env": "PDN"
        },
        {
            "ApplicationCode": "code1-app",
            "ApplicationName": "Example Application Name 1",
            "ApplicationType": "Example Application type 1",
            "ApplicationTag": "Example Application tag 1",
            "ApplicationDescription": "Example Application description 1",
            "Env": "DEV"
        }
    ]
}
```

Then, the remote config settings should look similar to this:
```json
"DEFECT_DOJO": {
    "HOST_DEFECT_DOJO": "http://localhost:8080",
    "LIMITS_QUERY": 100,
    "MAX_RETRIES_QUERY": 5,
    "REIMPORT_SCAN": false,
    "CMDB": {
        "USE_CMDB": true,
        "HOST_CMDB": "http://host_cmdb_example",
        "REGEX_EXPRESSION_CMDB": "^([^-]+)",
        "CMDB_MAPPING_PATH": "/path/mapping_cmdb.json",
        "CMDB_MAPPING": {
            "PRODUCT_TYPE_NAME": "ApplicationType",
            "PRODUCT_NAME": "ApplicationName",
            "TAG_PRODUCT": "ApplicationTag",
            "PRODUCT_DESCRIPTION": "ApplicationDescription",
            "CODIGO_APP": "ApplicationCode"
        },
        "CMDB_REQUEST_RESPONSE": {
            "HEADERS": {
                "Content-Type": "application/json",
                "Api-Key": "tokenvalue"
            },
            "METHOD": "GET",
            "PARAMS": {
                "appCode": "codappvalue"
            },
            "RESPONSE": ["value", 0]
        }
    }
}
```

**Let’s detail the description for the elements under the CMDB key:**

- *USE_CMDB:* The value is a boolean, indicating whether or not CMDB will be used.

- *HOST_CMDB:* The URL of the API for querying the CMDB.

- *REGEX_EXPRESSION_CMDB:* Regular expression.

- *CMDB_MAPPING_PATH:* Location of the mapping for possible product types.

- *CMDB_MAPPING:* Element containing the equivalent mappings between DefectDojo and the CMDB.

- *CMDB_REQUEST_RESPONSE:* Contains the necessary elements to make a request to the CMDB.

- *HEADERS:* Headers required to make the request. Note that the authentication type must be via Api-Key. The value "tokenvalue" should remain as is, as it is necessary for replacing the token.

- *METHOD:* Can be either POST or GET.

- *PARAMS:* Used if the selected METHOD is GET. The value "codappvalue" should remain as is, as it is necessary for replacement.

- *BODY:* Used if the selected METHOD is POST. The value "codappvalue" should remain as is, as it is necessary for replacement.

#### Without Using CMDB:
For this case, three environment variables must be created according to the DevOps platform.
```bash
## Platform local
DET_VM_PRODUCT_TYPE_NAME="Example product type name"
DET_VM_PRODUCT_NAME="Example product type name"
DET_VM_PRODUCT_DESCRIPTION="Example product descrition"

## Platform azure
VM_PRODUCT_TYPE_NAME="Example product type name"
VM_PRODUCT_NAME="Example product type name"
VM_PRODUCT_DESCRIPTION="Example product descrition"

## Platform github
VM_PRODUCT_TYPE_NAME="Example product type name"
VM_PRODUCT_NAME="Example product type name"
VM_PRODUCT_DESCRIPTION="Example product descrition"
```

The remote config settings should look similar to this:
```json
    "DEFECT_DOJO": {
        "HOST_DEFECT_DOJO": "http://localhost:8080",
        "LIMITS_QUERY": 100,
        "MAX_RETRIES_QUERY": 5,
        "REIMPORT_SCAN": false,
        "CMDB": {
            "USE_CMDB": false,
            "REGEX_EXPRESSION_CMDB": "^([^-]+)",
        }
    }
```

## **engine_dast**

Module is responsible for orchestrating Dynamic Application Security Testing (DAST) within the DevSecOps Engine Tools platform. It automates the execution of DAST tools, processes scan configurations, manages authentication flows, and integrates results for further risk analysis and reporting

For more information about structure remote config for this module, [engine dast](../modules/engine_dast.md)

## **engine_integrations**

The engine_integrations module enables the integration of DevSecOps Engine Tools with external systems and platforms, focusing on orchestrating and automating reporting and data exchange processes. It is designed to be extensible, allowing new integrations to be added as needed.

### **report_sonar**
For more information about structure remote config for this integration, [copacetic](../modules/engine_integrations/copacetic.md)

### **report_sonar**
For more information about structure remote config for this integration, [report sonar](../modules/engine_integrations/report_sonar.md)

## **engine_risk**
Module for prioritizing the resolution of findings reported in Vulnerability Management.

For more information about structure remote config for this module, [engine risk](../modules/engine_risk.md)

## **engine_sast**

### **engine_code**

The engine_code module is responsible for orchestrating Static Application Security Testing (SAST) within the DevSecOps Engine Tools platform. It automates the execution of SAST tools, processes code scan configurations, manages exclusions, and integrates results for further risk analysis and reporting.

For more information about structure remote config for this module, [engine code](../modules/engine_sast/engine_code.md)

### **engine_iac**

Static infrastructure analysis (k8s, dockerfile, cft) is a process that detects vulnerabilities in an application's defined infrastructure. This automated process is part of Bancolombia's DevSecOps practices, which evaluate security, code quality, and compliance.

For more information about structure remote config for this module, [engine iac](../modules/engine_sast/engine_iac.md)

### **engine_secret**

Secret scanning is a process that detects vulnerabilities in the application's source code. This automated process is part of Bancolombia's DevSecOps practices, through which security, code quality, and compliance are evaluated.

For more information about structure remote config for this module, [engine secret](../modules/engine_sast/engine_secret.md)

## **engine_sca**

### **engine_container**

Container Security Analysis (CSA) is a practice focused on ensuring the integrity, confidentiality, and availability of container-based applications, promoting a security culture from the early stages of development through deployment and production operations.

For more information about structure remote config for this module, [engine container](../modules/engine_sca/engine_container.md)

### **engine_dependencies**

Software Composition Analysis (SCA) is a process that detects compromised or vulnerable open-source components used in an application's source code. This automated process is part of Bancolombia's DevSecOps practices, through which security, code quality, and compliance are evaluated.

For more information about structure remote config for this module, [engine dependencies](../modules/engine_sca/engine_dependencies.md)

## **vulnerability_management**

## **engine_sca/engine_function**

Function SCA scans the packaged code of serverless functions (.zip files) for AWS Lambda and Azure Functions to identify vulnerabilities (CVEs) and compliance findings.
This capability uses Prisma Cloud (twistcli) and is part of DevSecOps practices to assess security, quality, and compliance.

### Configuration

> /engine_sca/engine_function/ConfigTool.json
```json
{


  "PRISMA_CLOUD": {
    "PRISMA_CONSOLE_URL": "https://<your-console>",
    "PRISMA_API_VERSION": "v1",
    "TWISTCLI_PATH": "twistcli.exe"                      // Relative path to save/read twistcli

  },
  "IGNORE_SEARCH_PATTERN": "(.*_legacy|.*_skip)",        // Optional: regex to skip analysis
  "MESSAGE_INFO_ENGINE_FUNCTION": "message custom",
  "THRESHOLD": {
    "VULNERABILITY": {
      "Critical": 1,
      "High": 3,
      "Medium": 10,
      "Low": 999
    },
    "COMPLIANCE": {
      "Critical": 1
    },
    "CVE": ["CVE-2024-0001"]
  }
}
```
Required pipeline variables

* PRISMA_ACCESS_KEY: Access Key (plaintext).

* PRISMA_SECRET_KEY: Secret Key (stored as a secret variable or in Secret Manager).

* (Optional) PRISMA_CONSOLE_URL to override the value in config.

The engine reads the Access Key using the variable name configured in PRISMA_ACCESS_KEY, and obtains the Secret Key either from parameters or your pipeline’s secrets (depending on your implementation).

### Exclusions

> /engine_sca/engine_function/Exclusions.json
#### **By Component**

The object key is the pipeline name (Build/Release). You can declare:
 > TOOL:
    - id: Prisma rule
    - cve_id: CVE
    - where: all or dependency to be excluded
    - create_date: creation date (daymonthyear)
    - expired_date: expiration date (daymonthyear)
    - severity: Severity of the finding
    - hu: User Story identifier supporting the configured exception.
 
 > SKIP_TOOL
    - create_date: creation date (daymonthyear)
    - expired_date: expiration date (daymonthyear)
    - hu: User Story identifier supporting the configured exception.

 > SKIP_FILES
    - files: Array of file extensions to exclude
    - create_date: creation date (daymonthyear)
    - expired_date: expiration date (daymonthyear)
    - hu: User Story identifier supporting the configured exception.

 > THRESHOLD
    - VULNERABILITY: new defined levels (Critical, High, Medium, Low)
    - Compliance: new defined levels (Critical)
    - CVE: List of CVEs
    - create_date: creation date (daymonthyear)
    - expired_date: expiration date (daymonthyear)
    - reason: reason for the threshold exclusion
    - hu: User Story identifier supporting the configured exception.



```json
{
  "NU0000_Build_Functions": {
    "SKIP_TOOL": {
      "create_date": "24012024",
      "expired_date": "30012024",
      "hu": "HU-12345"
    },
    "PRISMA": [
      {
        "id": "RULE-PRISMA-0001",
        "cve_id": "CVE-2024-1111",
        "where": "all",
        "create_date": "18112023",
        "expired_date": "18032024",
        "severity": "HIGH",
        "hu": "HU-67890",
        "reason": "False Positive"
      }
    ],
    "SKIP_FILES": {
      "files": ["zip"],
      "create_date": "19022024",
      "expired_date": "undefined",
      "hu": "HU-99999"
    },
    "THRESHOLD": {
      "VULNERABILITY": {
        "Critical": 2,
        "High": 5,
        "Medium": 10,
        "Low": 999
      },
      "COMPLIANCE": { "Critical": 1 },
      "CVE": [],
      "create_date": "26092024",
      "expired_date": "30062025",
      "reason": "Context-specific threshold",
      "hu": "HU-55555"
    }
  }
}
```
#### **By All Policy**

The object key is All and it applies to all pipelines.

```json
{
  "All": {
    "PRISMA": [
      {
        "id": "RULE-PRISMA-GLOBAL-01",
        "cve_id": "CVE-2023-6378",
        "where": "all",
        "create_date": "18112023",
        "expired_date": "18032024",
        "hu": "HU-43210",
        "reason": "False Positive"
      }
    ]
  }
}

```


## **vulnerability_management/cmdb_mapping**

Mapping configuration for the names of the evcs obtained from the cmdb, to centralize a single name and have unified product types in Vulnerability Management.

 > types_product:
  - "CMDB Name" : "Unique product type name for Vulnerability Management"

> Example vulnerability_management/cmdb_mapping.json
```json
{
  "types_product": {
    "IT ARCHITECTURE": "PT1 - ARCHITECTURE",
    "SOFTWARE ENGINEERING": "PT2 - IT ENGINEERING"
  }
}
```