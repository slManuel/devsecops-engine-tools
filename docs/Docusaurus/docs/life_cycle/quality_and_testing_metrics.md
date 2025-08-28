---
sidebar_position: 4
---


# Quality Metrics and Testing

This section details how we measure software quality, combining quality metrics and testing. The goal is to ensure that the code is of high quality and to validate the behavior of the system through different types of testing.

---

## 1. Source Code Management and Version Control

We use Trunk Based Development as our version control methodology. This approach maintains a single main branch (trunk or main) where developers frequently integrate their changes. Small, continuous changes help identify problems quickly and facilitate continuous integration.

Each change to the main branch is made through pull requests that must be reviewed and approved before being integrated.

---

## 2. Unit Test Coverage

Our library undergoes rigorous unit testing, maintaining a minimum coverage of 70%. This practice ensures the reliability and maintainability of the code by validating that individual components function as expected.

We use coverage measurement tools integrated into our CI/CD pipeline to ensure that this threshold is maintained. No code can be integrated into the main branch if it does not meet the established coverage criteria.

---

## 3. Static Code Analysis and Technical Debt

Static code analysis is integrated into our development process to identify quality and security issues before the code reaches production. We use specialized tools for this analysis that run automatically on every integration.

We actively manage technical debt to keep it under control.

---