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