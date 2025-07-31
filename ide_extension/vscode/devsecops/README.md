# DevSecOps Engine Tools

[![Maintained by Bancolombia](https://img.shields.io/badge/maintained_by-Bancolombia-yellow)](#)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/bancolombia/devsecops-engine-tools/intellij-build.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=bancolombia_devsecops-engine-tool-intellij&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=bancolombia_devsecops-engine-tool-intellij)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=bancolombia_devsecops-engine-tool-intellij&metric=coverage)](https://sonarcloud.io/summary/new_code?id=bancolombia_devsecops-engine-tool-intellij)
![Downloads](https://img.shields.io/jetbrains/plugin/d/25069-devsecops-engine-tools)
![Rating](https://img.shields.io/jetbrains/plugin/r/rating/25069-devsecops-engine-tools)
![Version](https://img.shields.io/jetbrains/plugin/v/25069-devsecops-engine-tools)

---

## 🚀 Description

**DevSecOps Engine Tools** is a Visual Studio Code extension developed by Bancolombia to detect security vulnerabilities early in the development lifecycle without depending solely on pipelines.

It enables static scans for **Infrastructure as Code (IaC)**, **Container Images**, and **Dependencies**, using custom and industry-recognized tools. It highlights vulnerable lines in the code, suggests fixes with GitHub Copilot, and presents interactive results.

---

## 📦 Key Features 

### 🛠️ Infrastructure as Code (IaC)

- Scan files such as Terraform, Dockerfiles, Kubernetes manifests, and CloudFormation templates
- File-based findings panel
- Highlights the vulnerable line directly in the editor
- Hover support for vulnerability details and contextual Copilot fix
- Support for environment variable substitution (as in pipeline configs)
- No additional configuration required beyond the initial setup  

### 🐳 Container

- Scans locally available images
- Displays scan findings per image
- Right-side panel with detailed vulnerability info for the selected image

### 📦 Dependencies

- Analyze project dependencies with:
  - [JFrog Xray](https://jfrog.com/xray/)
  - [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- Detect known CVEs in third-party libraries
- Compatible with popular package managers (Maven, Gradle, npm, etc.)
- Results are displayed in an organized findings panel with actionable insights

---

## 🧠 AI Integration

The extension integrates with **GitHub Copilot** to:
- Offer automated remediation suggestions (`Fix using Copilot`)
- Explain vulnerabilities in plain language (`Explain`)
- Apply fixes directly and reflect changes within the file

---

## 📥 Installation

1. Install the extension from the [VSCode Marketplace](https://marketplace.visualstudio.com/items?itemName=bancolombia.devsecops-engine-tools)
2. Make sure the following are installed:
   - ✅ [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
   - ✅ Docker (Windows/Linux) or Podman (Mac)
3. Activate Docker before scanning container images
4. From the editor:
   - Select the folder to scan
   - View results in the left panel
   - Explore details and suggestions in the right webview

---

## 🧪 Usage Considerations

- Validate that results shown in the webview match the expected file and line
- Configure custom environment variables within workspace settings
- Feedback is crucial to evolve the tool (see below)

---

## 📚 Additional Resources

- [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)
- [Visual Studio Code Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
- [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

---

**Thanks for being part of the shift toward secure development from day one!**

---
