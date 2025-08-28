---
sidebar_position: 4
---

# Security

In this section, we detail the different security tactics we use in the project, ranging from secret management to protection against attacks. Our goal is to ensure that all project infrastructure, data, and processes are protected from external and internal threats, complying with security best practices.

## 1. Management of Secrets and Security Variables

Secrets and security variables are managed centrally through dedicated services to prevent their exposure in code or configuration files:

- **AWS Secrets Manager**: We use this service to automatically store and rotate secrets.

- **GitHub Secrets:** Environment variables and secrets required for continuous integration are stored as GitHub Secrets.

## 2. Encryption

We implement multi-level encryption to protect information:

- **Encryption in transit:** All communications between services use TLS 1.3 to ensure confidentiality.

- **Encryption at rest**: Data stored in S3 buckets, and other storage services is encrypted using AWS KMS.

## 3. Security Monitoring and Auditing

We maintain constant vigilance over our infrastructure:

- **Centralized logging**: All security events are logged and stored centrally.

- **Automatic alerts**: Notifications are configured for suspicious activity.

- **Continuous scanning**: Regular analysis of vulnerabilities and insecure configurations.

